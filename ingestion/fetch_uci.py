"""
UCI Dataset Fetcher

This script downloads the Individual Household Electric Power Consumption dataset
from the UCI Machine Learning Repository.

Dataset Details:
- Source: UCI ML Repository
- Measurements: 2,075,259 records (2006-2010)
- Frequency: 1-minute intervals
- Variables: Global active power, reactive power, voltage, current, sub-metering
- Size: ~20MB compressed, ~130MB uncompressed

Usage:
    python ingestion/fetch_uci.py --output data/raw/household_power.zip

What this script does:
1. Downloads the dataset from UCI
2. Verifies file integrity (checksum)
3. Saves to data/raw/ folder
4. Logs download metadata
"""

import argparse
import hashlib
import logging
import os
import sys
from pathlib import Path
from typing import Optional
from urllib.request import urlretrieve

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Dataset configuration
UCI_DATASET_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip"
EXPECTED_SHA256 = None  # TODO: Add checksum after first download

# Alternative: Use a stable mirror or your own hosted copy
# UCI_DATASET_URL = "https://your-mirror.com/household_power_consumption.zip"


def calculate_sha256(filepath: Path) -> str:
    """
    Calculate SHA256 hash of a file.
    
    This helps verify that the download wasn't corrupted.
    Like checking that a package you received wasn't damaged in shipping.
    
    Args:
        filepath: Path to the file to hash
        
    Returns:
        SHA256 hash as hexadecimal string
    """
    sha256_hash = hashlib.sha256()
    
    # Read file in chunks to handle large files efficiently
    with open(filepath, "rb") as f:
        # Read 4KB at a time (memory efficient)
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def download_with_progress(url: str, output_path: Path) -> None:
    """
    Download file with progress reporting.
    
    Args:
        url: URL to download from
        output_path: Where to save the file
    """
    def report_progress(block_num, block_size, total_size):
        """Show download progress"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(100, (downloaded / total_size) * 100)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\rDownloading: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end="")
    
    logger.info(f"Downloading from {url}")
    urlretrieve(url, output_path, reporthook=report_progress)
    print()  # New line after progress


def fetch_uci_dataset(
    output_path: Optional[Path] = None,
    verify_checksum: bool = True,
    force_download: bool = False
) -> Path:
    """
    Download UCI household power consumption dataset.
    
    Args:
        output_path: Where to save the dataset (default: data/raw/household_power.zip)
        verify_checksum: Whether to verify file integrity after download
        force_download: Re-download even if file exists
        
    Returns:
        Path to downloaded file
        
    Raises:
        ValueError: If checksum verification fails
    """
    # Set default output path
    if output_path is None:
        output_path = Path("data/raw/household_power.zip")
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file already exists
    if output_path.exists() and not force_download:
        logger.info(f"Dataset already exists at {output_path}")
        logger.info("Use --force to re-download")
        return output_path
    
    # Download the dataset
    try:
        download_with_progress(UCI_DATASET_URL, output_path)
        logger.info(f"Download complete: {output_path}")
        
        # Get file size
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        logger.info(f"File size: {file_size_mb:.2f} MB")
        
        # Verify checksum if requested and expected hash is known
        if verify_checksum and EXPECTED_SHA256:
            logger.info("Verifying file integrity...")
            actual_hash = calculate_sha256(output_path)
            
            if actual_hash != EXPECTED_SHA256:
                raise ValueError(
                    f"Checksum mismatch!\n"
                    f"Expected: {EXPECTED_SHA256}\n"
                    f"Got:      {actual_hash}\n"
                    f"File may be corrupted. Please delete and re-download."
                )
            
            logger.info("✓ Checksum verified")
        elif verify_checksum:
            # Calculate and log hash for first-time setup
            actual_hash = calculate_sha256(output_path)
            logger.info(f"SHA256: {actual_hash}")
            logger.info("Tip: Add this hash to EXPECTED_SHA256 for future verification")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        # Clean up partial download
        if output_path.exists():
            output_path.unlink()
        raise


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Download UCI household power consumption dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download to default location (data/raw/)
  python ingestion/fetch_uci.py
  
  # Download to specific location
  python ingestion/fetch_uci.py --output /path/to/save/dataset.zip
  
  # Force re-download
  python ingestion/fetch_uci.py --force
  
  # Skip checksum verification
  python ingestion/fetch_uci.py --no-verify
        """
    )
    
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw/household_power.zip"),
        help="Output path for downloaded file (default: data/raw/household_power.zip)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if file exists"
    )
    
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip checksum verification"
    )
    
    args = parser.parse_args()
    
    try:
        output_file = fetch_uci_dataset(
            output_path=args.output,
            verify_checksum=not args.no_verify,
            force_download=args.force
        )
        
        logger.info("=" * 60)
        logger.info("SUCCESS! Dataset ready for processing")
        logger.info(f"Location: {output_file.absolute()}")
        logger.info("Next step: Run ingestion/etl.py to process the data")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to fetch dataset: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
