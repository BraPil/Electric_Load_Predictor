"""
ETL Pipeline for UCI Household Power Consumption Dataset

ETL = Extract, Transform, Load

This script:
1. EXTRACT: Unzips and reads the raw UCI dataset
2. TRANSFORM: Cleans, validates, and processes the data
3. LOAD: Saves processed data to Postgres database

What gets transformed:
- Parse timestamps into proper datetime format
- Handle missing values (marked as '?' in dataset)
- Convert units to standard format
- Add quality flags for suspicious readings
- Resample to hourly intervals (from 1-minute)

Usage:
    # Process all data
    python ingestion/etl.py --input data/raw/household_power.zip
    
    # Process only recent data (faster for testing)
    python ingestion/etl.py --input data/raw/household_power.zip --limit 10000
"""

import argparse
import logging
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataQualityError(Exception):
    """Raised when data quality checks fail"""
    pass


def extract_dataset(zip_path: Path) -> pd.DataFrame:
    """
    Extract dataset from ZIP file and load into pandas DataFrame.
    
    The UCI dataset structure:
    - File: household_power_consumption.txt
    - Format: semicolon-separated values (;)
    - Missing values: marked as '?'
    - Date format: dd/mm/yyyy
    - Time format: hh:mm:ss
    
    Args:
        zip_path: Path to the ZIP file
        
    Returns:
        Raw DataFrame with all columns
    """
    logger.info(f"Extracting dataset from {zip_path}")
    
    if not zip_path.exists():
        raise FileNotFoundError(f"Dataset not found: {zip_path}")
    
    # Extract ZIP file
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # The ZIP contains a single .txt file
        txt_filename = "household_power_consumption.txt"
        
        # Read directly from ZIP without extracting to disk
        with zip_ref.open(txt_filename) as f:
            logger.info(f"Reading {txt_filename}...")
            
            # Read CSV with specific settings for this dataset
            df = pd.read_csv(
                f,
                sep=';',                    # Columns separated by semicolon
                na_values='?',              # '?' means missing data
                parse_dates={'timestamp': ['Date', 'Time']},  # Combine Date+Time
                dayfirst=True,              # Date format is dd/mm/yyyy
                low_memory=False            # Read entire file at once
            )
    
    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    return df


def transform_data(df: pd.DataFrame, limit: Optional[int] = None) -> pd.DataFrame:
    """
    Clean and transform the raw data.
    
    Transformations:
    1. Set timestamp as index
    2. Handle missing values
    3. Add quality flags
    4. Resample to hourly intervals
    5. Add derived features
    
    Args:
        df: Raw DataFrame from extract step
        limit: Maximum number of rows to process (for testing)
        
    Returns:
        Transformed DataFrame ready for database
    """
    logger.info("Starting data transformation...")
    
    # Limit rows if requested (useful for testing)
    if limit:
        logger.info(f"Limiting to first {limit:,} rows")
        df = df.head(limit)
    
    # 1. Set timestamp as index
    df = df.set_index('timestamp')
    df.index.name = 'timestamp'
    
    # 2. Report missing values
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        logger.warning(f"Missing values found:\n{missing_counts[missing_counts > 0]}")
    
    # 3. Add quality flags
    # Flag rows with any missing critical measurements
    critical_columns = ['Global_active_power', 'Global_reactive_power', 'Voltage']
    df['quality_flag'] = 'OK'
    df.loc[df[critical_columns].isnull().any(axis=1), 'quality_flag'] = 'MISSING_DATA'
    
    # Flag suspicious values (e.g., voltage outside normal range)
    # Typical household voltage: 220-240V in Europe
    voltage_mask = (df['Voltage'] < 200) | (df['Voltage'] > 260)
    df.loc[voltage_mask, 'quality_flag'] = 'SUSPICIOUS_VOLTAGE'
    
    # 4. Fill missing values with forward fill (use last known good value)
    # This is reasonable for 1-minute gaps in power consumption
    df_filled = df.fillna(method='ffill', limit=5)  # Max 5 consecutive fills
    
    # 5. Resample to hourly intervals (average of 1-minute readings)
    logger.info("Resampling to hourly intervals...")
    df_hourly = df_filled.resample('H').agg({
        'Global_active_power': 'mean',
        'Global_reactive_power': 'mean',
        'Voltage': 'mean',
        'Global_intensity': 'mean',
        'Sub_metering_1': 'sum',      # Sum for energy consumption
        'Sub_metering_2': 'sum',
        'Sub_metering_3': 'sum',
        'quality_flag': lambda x: 'OK' if (x == 'OK').all() else 'DEGRADED'
    })
    
    # 6. Add derived features
    # Total power consumption (kW)
    df_hourly['total_power_kw'] = df_hourly['Global_active_power']
    
    # Hour of day (0-23)
    df_hourly['hour_of_day'] = df_hourly.index.hour
    
    # Day of week (0=Monday, 6=Sunday)
    df_hourly['day_of_week'] = df_hourly.index.dayofweek
    
    # Month (1-12)
    df_hourly['month'] = df_hourly.index.month
    
    # Is weekend? (useful for load prediction)
    df_hourly['is_weekend'] = df_hourly['day_of_week'].isin([5, 6]).astype(int)
    
    logger.info(f"Transformation complete: {len(df_hourly):,} hourly records")
    
    return df_hourly


def validate_data(df: pd.DataFrame) -> None:
    """
    Run quality checks on transformed data.
    
    Checks:
    - No duplicate timestamps
    - Reasonable value ranges
    - No excessive missing data
    - Chronological order
    
    Args:
        df: Transformed DataFrame
        
    Raises:
        DataQualityError: If any check fails
    """
    logger.info("Running data quality checks...")
    
    # Check 1: No duplicate timestamps
    if df.index.duplicated().any():
        raise DataQualityError("Duplicate timestamps found!")
    
    # Check 2: Chronological order
    if not df.index.is_monotonic_increasing:
        raise DataQualityError("Timestamps are not in chronological order!")
    
    # Check 3: Reasonable value ranges
    power_issues = (df['Global_active_power'] < 0) | (df['Global_active_power'] > 20)
    if power_issues.sum() > 0:
        logger.warning(f"Found {power_issues.sum()} records with suspicious power values")
    
    voltage_issues = (df['Voltage'] < 200) | (df['Voltage'] > 260)
    if voltage_issues.sum() > 0:
        logger.warning(f"Found {voltage_issues.sum()} records with suspicious voltage values")
    
    # Check 4: Not too many missing values
    missing_pct = (df.isnull().sum() / len(df)) * 100
    if (missing_pct > 10).any():
        problematic = missing_pct[missing_pct > 10]
        raise DataQualityError(f"Too many missing values:\n{problematic}")
    
    logger.info("✓ All quality checks passed")


def load_to_database(
    df: pd.DataFrame,
    table_name: str = "raw_measurements",
    db_url: Optional[str] = None,
    if_exists: str = "append"
) -> None:
    """
    Load data into PostgreSQL database.
    
    Args:
        df: DataFrame to load
        table_name: Name of table to create/append to
        db_url: Database connection URL (from environment if None)
        if_exists: What to do if table exists ('append', 'replace', 'fail')
    """
    # Get database URL from environment or use default
    if db_url is None:
        import os
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://voltedge:voltedge@localhost:5432/voltedge"
        )
    
    logger.info(f"Connecting to database...")
    logger.info(f"Loading {len(df):,} rows into table '{table_name}'...")
    
    try:
        # Create database connection
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"Connected to: {version[:50]}...")
        
        # Load data to database
        # Note: This creates the table if it doesn't exist
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=True,          # Include timestamp index
            index_label='timestamp',
            method='multi',      # Faster bulk insert
            chunksize=1000       # Insert 1000 rows at a time
        )
        
        logger.info(f"✓ Successfully loaded {len(df):,} rows to '{table_name}'")
        
    except Exception as e:
        logger.error(f"Database load failed: {e}")
        logger.info("Tip: Make sure PostgreSQL is running (docker compose up)")
        raise


def save_to_parquet(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save processed data to Parquet file (fast columnar format).
    
    This is useful for:
    - Archiving processed data
    - Faster loading for analysis
    - Sharing data with other tools
    
    Args:
        df: DataFrame to save
        output_path: Where to save the file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving processed data to {output_path}")
    df.to_parquet(output_path, compression='snappy', index=True)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"✓ Saved {file_size_mb:.2f} MB to {output_path}")


def run_etl(
    input_path: Path,
    limit: Optional[int] = None,
    skip_db: bool = False,
    save_parquet: bool = True
) -> pd.DataFrame:
    """
    Run the complete ETL pipeline.
    
    Args:
        input_path: Path to ZIP file with raw data
        limit: Maximum rows to process (for testing)
        skip_db: Don't load to database (useful for testing)
        save_parquet: Save to parquet file
        
    Returns:
        Processed DataFrame
    """
    logger.info("=" * 60)
    logger.info("Starting ETL Pipeline")
    logger.info("=" * 60)
    
    # EXTRACT
    raw_df = extract_dataset(input_path)
    
    # TRANSFORM
    processed_df = transform_data(raw_df, limit=limit)
    
    # VALIDATE
    validate_data(processed_df)
    
    # LOAD - to database
    if not skip_db:
        try:
            load_to_database(processed_df, if_exists="replace")
        except Exception as e:
            logger.warning(f"Skipping database load: {e}")
            logger.info("Continuing with file-based storage...")
    
    # LOAD - to parquet file
    if save_parquet:
        output_path = Path("data/processed/household_power_hourly.parquet")
        save_to_parquet(processed_df, output_path)
    
    logger.info("=" * 60)
    logger.info("ETL Pipeline Complete!")
    logger.info(f"Processed {len(processed_df):,} hourly records")
    logger.info(f"Date range: {processed_df.index.min()} to {processed_df.index.max()}")
    logger.info("=" * 60)
    
    return processed_df


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="ETL pipeline for UCI household power dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process full dataset
  python ingestion/etl.py --input data/raw/household_power.zip
  
  # Quick test with first 10,000 rows
  python ingestion/etl.py --input data/raw/household_power.zip --limit 10000
  
  # Skip database load (save to files only)
  python ingestion/etl.py --input data/raw/household_power.zip --skip-db
        """
    )
    
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input ZIP file"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of rows to process (for testing)"
    )
    
    parser.add_argument(
        "--skip-db",
        action="store_true",
        help="Skip database load (save to files only)"
    )
    
    args = parser.parse_args()
    
    try:
        run_etl(
            input_path=args.input,
            limit=args.limit,
            skip_db=args.skip_db
        )
        return 0
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
