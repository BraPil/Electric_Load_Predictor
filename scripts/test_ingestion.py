"""
Ingestion Pipeline Test Runner

This script tests the complete data ingestion pipeline and logs all results.
It runs without requiring Docker/PostgreSQL by using the --skip-db option.

What this test does:
1. Downloads UCI dataset (if not already present)
2. Runs ETL pipeline with validation
3. Logs all operations with timestamps
4. Generates a test report with metrics
5. Validates output files exist and are correct size

Usage:
    python scripts/test_ingestion.py
    
    # Quick test with limited data
    python scripts/test_ingestion.py --limit 10000
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add project root to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.fetch_uci import fetch_uci_dataset
from ingestion.etl import run_etl

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ingestion_test.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)


class TestReport:
    """Container for test results and metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.steps = []
        self.metrics = {}
        self.errors = []
        self.warnings = []
    
    def log_step(self, step_name: str, status: str, duration: float = None, details: str = None):
        """Log a test step"""
        step = {
            'name': step_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'details': details
        }
        self.steps.append(step)
        
        # Also log to console
        status_icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        duration_str = f" ({duration:.2f}s)" if duration else ""
        logger.info(f"{status_icon} {step_name}: {status}{duration_str}")
        if details:
            logger.info(f"  Details: {details}")
    
    def add_metric(self, name: str, value: Any):
        """Record a metric"""
        self.metrics[name] = value
        logger.info(f"📊 Metric - {name}: {value}")
    
    def add_error(self, error: str):
        """Record an error"""
        self.errors.append(error)
        logger.error(f"❌ Error: {error}")
    
    def add_warning(self, warning: str):
        """Record a warning"""
        self.warnings.append(warning)
        logger.warning(f"⚠️  Warning: {warning}")
    
    def generate_summary(self) -> str:
        """Generate test summary report"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        passed = sum(1 for s in self.steps if s['status'] == 'PASS')
        failed = sum(1 for s in self.steps if s['status'] == 'FAIL')
        
        summary = f"""
{'='*80}
INGESTION PIPELINE TEST REPORT
{'='*80}
Start Time:     {self.start_time.isoformat()}
Duration:       {duration:.2f} seconds
Total Steps:    {len(self.steps)}
Passed:         {passed}
Failed:         {failed}
Warnings:       {len(self.warnings)}
{'='*80}

METRICS:
"""
        for name, value in self.metrics.items():
            summary += f"  {name:30s}: {value}\n"
        
        summary += f"\n{'='*80}\nSTEP DETAILS:\n"
        for i, step in enumerate(self.steps, 1):
            status_icon = "✓" if step['status'] == "PASS" else "✗"
            summary += f"\n{i}. {status_icon} {step['name']} - {step['status']}\n"
            if step['duration_seconds']:
                summary += f"   Duration: {step['duration_seconds']:.2f}s\n"
            if step['details']:
                summary += f"   {step['details']}\n"
        
        if self.warnings:
            summary += f"\n{'='*80}\nWARNINGS:\n"
            for warn in self.warnings:
                summary += f"  ⚠️  {warn}\n"
        
        if self.errors:
            summary += f"\n{'='*80}\nERRORRS:\n"
            for err in self.errors:
                summary += f"  ❌ {err}\n"
        
        summary += f"\n{'='*80}\n"
        summary += f"Overall Status: {'✅ PASS' if failed == 0 else '❌ FAIL'}\n"
        summary += f"{'='*80}\n"
        
        return summary


def test_fetch_dataset(report: TestReport, force: bool = False) -> Path:
    """Test dataset download"""
    logger.info("="*80)
    logger.info("STEP 1: Testing Dataset Download")
    logger.info("="*80)
    
    start = time.time()
    
    try:
        output_path = fetch_uci_dataset(
            output_path=Path("data/raw/household_power.zip"),
            verify_checksum=True,
            force_download=force
        )
        
        duration = time.time() - start
        
        # Validate file exists
        if not output_path.exists():
            raise FileNotFoundError(f"Download failed: {output_path} not found")
        
        # Check file size (should be ~20MB compressed)
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        if file_size_mb < 15 or file_size_mb > 30:
            report.add_warning(f"File size {file_size_mb:.2f}MB seems unusual (expected ~20MB)")
        
        report.log_step(
            "Download UCI Dataset",
            "PASS",
            duration,
            f"Size: {file_size_mb:.2f}MB, Location: {output_path}"
        )
        report.add_metric("Dataset Size (MB)", f"{file_size_mb:.2f}")
        
        return output_path
        
    except Exception as e:
        duration = time.time() - start
        report.log_step("Download UCI Dataset", "FAIL", duration, str(e))
        report.add_error(f"Download failed: {e}")
        raise


def test_etl_pipeline(report: TestReport, input_path: Path, limit: int = None):
    """Test ETL pipeline"""
    logger.info("="*80)
    logger.info("STEP 2: Testing ETL Pipeline")
    logger.info("="*80)
    
    start = time.time()
    
    try:
        # Run ETL with database skipped (no Docker needed)
        processed_df = run_etl(
            input_path=input_path,
            limit=limit,
            skip_db=True,
            save_parquet=True
        )
        
        duration = time.time() - start
        
        # Validate output
        if processed_df is None or len(processed_df) == 0:
            raise ValueError("ETL returned empty DataFrame")
        
        # Check output file exists
        output_parquet = Path("data/processed/household_power_hourly.parquet")
        if not output_parquet.exists():
            raise FileNotFoundError(f"Output file not created: {output_parquet}")
        
        output_size_mb = output_parquet.stat().st_size / (1024 * 1024)
        
        # Calculate metrics
        date_range = (processed_df.index.min(), processed_df.index.max())
        total_days = (date_range[1] - date_range[0]).days
        
        # Check for data quality
        quality_ok = (processed_df['quality_flag'] == 'OK').sum()
        quality_pct = (quality_ok / len(processed_df)) * 100
        
        report.log_step(
            "ETL Pipeline",
            "PASS",
            duration,
            f"Processed {len(processed_df):,} hourly records"
        )
        
        # Record detailed metrics
        report.add_metric("Records Processed", f"{len(processed_df):,}")
        report.add_metric("Date Range", f"{date_range[0].date()} to {date_range[1].date()}")
        report.add_metric("Total Days", total_days)
        report.add_metric("Output File Size (MB)", f"{output_size_mb:.2f}")
        report.add_metric("Quality OK (%)", f"{quality_pct:.1f}%")
        report.add_metric("Processing Rate (rec/sec)", f"{len(processed_df)/duration:.0f}")
        
        # Check data quality thresholds
        if quality_pct < 90:
            report.add_warning(f"Quality percentage is {quality_pct:.1f}% (expected >90%)")
        
        return processed_df
        
    except Exception as e:
        duration = time.time() - start
        report.log_step("ETL Pipeline", "FAIL", duration, str(e))
        report.add_error(f"ETL failed: {e}")
        raise


def test_data_validation(report: TestReport, df):
    """Test data validation using pydantic schemas"""
    logger.info("="*80)
    logger.info("STEP 3: Testing Data Validation")
    logger.info("="*80)
    
    start = time.time()
    
    try:
        from ingestion.data_quality import validate_dataframe
        
        # Run validation on sample (first 1000 rows to speed up)
        sample_size = min(1000, len(df))
        sample_df = df.head(sample_size)
        
        validation_report = validate_dataframe(sample_df)
        
        duration = time.time() - start
        
        # Check validation results
        if validation_report.success_rate < 95:
            report.add_warning(
                f"Validation success rate is {validation_report.success_rate:.1f}% "
                f"(expected >95%)"
            )
        
        report.log_step(
            "Data Validation",
            "PASS",
            duration,
            f"Success rate: {validation_report.success_rate:.1f}%"
        )
        
        report.add_metric("Validation Sample Size", sample_size)
        report.add_metric("Validation Success Rate (%)", f"{validation_report.success_rate:.1f}")
        
        if validation_report.error_summary:
            report.add_metric("Validation Errors", str(validation_report.error_summary))
        
    except Exception as e:
        duration = time.time() - start
        report.log_step("Data Validation", "FAIL", duration, str(e))
        report.add_error(f"Validation failed: {e}")
        raise


def test_output_files(report: TestReport):
    """Verify all expected output files exist"""
    logger.info("="*80)
    logger.info("STEP 4: Verifying Output Files")
    logger.info("="*80)
    
    start = time.time()
    
    expected_files = [
        Path("data/raw/household_power.zip"),
        Path("data/processed/household_power_hourly.parquet"),
    ]
    
    all_exist = True
    file_details = []
    
    for filepath in expected_files:
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            file_details.append(f"✓ {filepath} ({size_mb:.2f}MB)")
        else:
            file_details.append(f"✗ {filepath} (MISSING)")
            all_exist = False
    
    duration = time.time() - start
    
    if all_exist:
        report.log_step(
            "Output Files Check",
            "PASS",
            duration,
            "\n  " + "\n  ".join(file_details)
        )
    else:
        report.log_step(
            "Output Files Check",
            "FAIL",
            duration,
            "\n  " + "\n  ".join(file_details)
        )
        report.add_error("Some expected output files are missing")


def main():
    """Run complete ingestion pipeline test"""
    parser = argparse.ArgumentParser(
        description="Test the ingestion pipeline and generate report"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of rows to process (for quick testing)"
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Force re-download of dataset"
    )
    
    args = parser.parse_args()
    
    # Initialize test report
    report = TestReport()
    
    logger.info("╔" + "="*78 + "╗")
    logger.info("║" + " "*20 + "INGESTION PIPELINE TEST SUITE" + " "*29 + "║")
    logger.info("╚" + "="*78 + "╝")
    logger.info("")
    
    if args.limit:
        logger.info(f"🔧 Running in QUICK TEST mode (limit: {args.limit:,} rows)")
    else:
        logger.info(f"🔧 Running in FULL TEST mode (all data)")
    
    logger.info("")
    
    try:
        # Test 1: Download dataset
        dataset_path = test_fetch_dataset(report, force=args.force_download)
        
        # Test 2: Run ETL
        processed_df = test_etl_pipeline(report, dataset_path, limit=args.limit)
        
        # Test 3: Validate data
        test_data_validation(report, processed_df)
        
        # Test 4: Check output files
        test_output_files(report)
        
        # Generate final report
        summary = report.generate_summary()
        print(summary)
        
        # Save report to file
        report_path = Path("ingestion_test_report.txt")
        with open(report_path, 'w') as f:
            f.write(summary)
        
        logger.info(f"📄 Full report saved to: {report_path.absolute()}")
        logger.info(f"📄 Detailed log saved to: ingestion_test.log")
        
        # Return exit code based on test results
        if report.errors:
            logger.error("❌ Tests FAILED - see errors above")
            return 1
        else:
            logger.info("✅ All tests PASSED!")
            return 0
    
    except Exception as e:
        logger.error(f"💥 Test suite crashed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
