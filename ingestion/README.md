# Data Ingestion Pipeline

This module handles downloading, validating, and loading the UCI Individual Household Electric Power Consumption dataset.

## 📊 Dataset Information

- **Source**: [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/individual+household+electric+power+consumption)
- **Size**: ~20MB compressed, ~130MB uncompressed
- **Records**: 2,075,259 measurements (2006-2010)
- **Frequency**: 1-minute intervals → resampled to hourly
- **Location**: Single household near Paris, France

### Measurements Included

| Column | Description | Unit |
|--------|-------------|------|
| Global_active_power | Household total active power | kilowatts (kW) |
| Global_reactive_power | Household total reactive power | kilovolt-amps reactive (kVAr) |
| Voltage | Average voltage | volts (V) |
| Global_intensity | Average current intensity | amperes (A) |
| Sub_metering_1 | Kitchen energy consumption | watt-hours (Wh) |
| Sub_metering_2 | Laundry room energy consumption | watt-hours (Wh) |
| Sub_metering_3 | Water heater & AC energy consumption | watt-hours (Wh) |

## 🚀 Quick Start

### Step 1: Download Dataset

```bash
# Using Python directly
python ingestion/fetch_uci.py

# Or using make (if installed)
make ingest
```

This downloads `household_power.zip` to `data/raw/`.

### Step 2: Process Data (ETL)

```bash
# Process full dataset (~2M records → ~35K hourly records)
python ingestion/etl.py --input data/raw/household_power.zip

# Quick test with limited data
python ingestion/etl.py --input data/raw/household_power.zip --limit 10000
```

This creates:
- Database table: `raw_measurements` (if PostgreSQL is running)
- Parquet file: `data/processed/household_power_hourly.parquet`

## 📁 Module Structure

```
ingestion/
├── __init__.py           # Package initialization
├── fetch_uci.py          # Download dataset from UCI
├── etl.py                # Extract, Transform, Load pipeline
├── data_quality.py       # Pydantic validation schemas
└── README.md             # This file
```

## 🔍 What Each Script Does

### fetch_uci.py

**Purpose**: Download the raw dataset

**Features**:
- Downloads from UCI repository
- Progress bar during download
- SHA256 checksum verification (integrity check)
- Skips download if file already exists

**Usage**:
```bash
# Basic usage
python ingestion/fetch_uci.py

# Custom output location
python ingestion/fetch_uci.py --output /path/to/save.zip

# Force re-download
python ingestion/fetch_uci.py --force
```

### etl.py

**Purpose**: Clean, transform, and load data

**Transformation Steps**:
1. **Extract**: Unzip and read CSV file
2. **Clean**: Handle missing values (marked as '?')
3. **Resample**: Convert 1-minute → hourly averages
4. **Derive**: Add features (hour, day, weekend flag)
5. **Validate**: Quality checks on ranges and completeness
6. **Load**: Save to database and/or parquet file

**Usage**:
```bash
# Full pipeline
python ingestion/etl.py --input data/raw/household_power.zip

# Test with limited data
python ingestion/etl.py --input data/raw/household_power.zip --limit 10000

# Skip database load (files only)
python ingestion/etl.py --input data/raw/household_power.zip --skip-db
```

**Output Schema**:
```
timestamp               (datetime, index)
Global_active_power     (float, kW)
Global_reactive_power   (float, kVAr)
Voltage                 (float, V)
Global_intensity        (float, A)
Sub_metering_1          (float, Wh)
Sub_metering_2          (float, Wh)
Sub_metering_3          (float, Wh)
quality_flag            (string: OK, DEGRADED, MISSING_DATA, SUSPICIOUS_VOLTAGE)
total_power_kw          (float, derived)
hour_of_day             (int, 0-23)
day_of_week             (int, 0=Mon, 6=Sun)
month                   (int, 1-12)
is_weekend              (int, 0 or 1)
```

### data_quality.py

**Purpose**: Define and validate data schemas using Pydantic

**Features**:
- `PowerMeasurement`: Schema defining valid measurement structure
- Automatic type conversion and validation
- Clear error messages when data is invalid
- Quality report generation

**Usage**:
```python
from ingestion.data_quality import PowerMeasurement, validate_dataframe
import pandas as pd

# Validate a single measurement
measurement = PowerMeasurement(
    timestamp="2006-12-16T17:00:00",
    global_active_power=4.2,
    voltage=235.0,
    # ... other fields
)

# Validate entire DataFrame
df = pd.read_parquet("data/processed/household_power_hourly.parquet")
report = validate_dataframe(df)
print(f"Success rate: {report.success_rate}%")
```

## 🔧 Data Quality Checks

The pipeline includes multiple quality checks:

### 1. Missing Value Handling
- Missing values (marked as `?`) are filled using forward-fill (max 5 gaps)
- Rows with critical missing data are flagged

### 2. Range Validation
- **Power**: 0-20 kW (typical household range)
- **Voltage**: 200-260 V (European standard ±10%)
- **Current**: 0-100 A (reasonable household max)

### 3. Integrity Checks
- No duplicate timestamps
- Chronological order maintained
- Less than 10% missing values per column

### 4. Quality Flags
- `OK`: All values normal
- `DEGRADED`: Some forward-filled values
- `MISSING_DATA`: Critical measurements missing
- `SUSPICIOUS_VOLTAGE`: Voltage outside normal range

## 📈 Expected Results

After processing, you should see:

```
Loaded 2,075,259 rows, 9 columns       (raw 1-minute data)
Resampling to hourly intervals...
Transformation complete: 35,064 hourly records
✓ All quality checks passed
✓ Successfully loaded 35,064 rows to 'raw_measurements'
✓ Saved 2.15 MB to data/processed/household_power_hourly.parquet

Date range: 2006-12-16 17:00:00 to 2010-11-26 21:00:00
```

## 🐛 Troubleshooting

### "Dataset not found"
```bash
# Make sure you've downloaded it first
python ingestion/fetch_uci.py
```

### "Database connection failed"
```bash
# Start PostgreSQL using docker
docker compose -f docker/docker-compose.yml up -d postgres

# Or skip database load
python ingestion/etl.py --input data/raw/household_power.zip --skip-db
```

### "Memory error"
```bash
# Process in smaller chunks
python ingestion/etl.py --input data/raw/household_power.zip --limit 100000
```

## 🔄 Workflow Integration

```bash
# Complete workflow
python ingestion/fetch_uci.py                              # Download
python ingestion/etl.py --input data/raw/household_power.zip  # Process

# Next steps (future phases)
python features/feature_store.py   # Feature engineering
python training/train_models.py    # Train ML models
```

## 📝 Notes

- **Time Zone**: Dataset uses UTC (Paris local time not converted)
- **Resampling**: Averages for power/voltage, sums for sub-metering
- **Performance**: Full ETL takes ~2-3 minutes on modern hardware
- **Storage**: Parquet file is ~98% smaller than CSV (compressed columnar format)

## 🎯 Next Phase

After ingestion, move to **Phase 3: Feature Engineering** to create:
- Lag features (previous hour's consumption)
- Rolling statistics (7-day average)
- Seasonal patterns (time of day, day of week effects)
- Weather integration (if external data available)
