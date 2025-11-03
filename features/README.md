# Feature Engineering Module

## Overview

This module transforms hourly electric load data into ML-ready features for time series forecasting. It implements best practices for temporal feature engineering, including lag features, rolling statistics, seasonal patterns, and cyclical encoding.

## Features Created

### 1. Lag Features (Autoregressive)
Captures temporal dependencies by looking back in time:
- `total_power_kw_lag_1h` - Previous hour's power consumption
- `total_power_kw_lag_24h` - Same hour yesterday (daily pattern)
- `total_power_kw_lag_168h` - Same hour last week (weekly pattern)

**Rationale**: Electric load exhibits strong autocorrelation. Recent consumption is highly predictive of future consumption.

### 2. Rolling Window Statistics
Captures trends and volatility over different time horizons:

**24-hour window (daily patterns)**:
- `total_power_kw_rolling_mean_24h` - Average load over past day
- `total_power_kw_rolling_std_24h` - Volatility over past day
- `total_power_kw_rolling_min_24h` - Minimum load over past day
- `total_power_kw_rolling_max_24h` - Peak load over past day

**168-hour window (weekly patterns)**:
- `total_power_kw_rolling_mean_168h` - Average load over past week
- `total_power_kw_rolling_std_168h` - Volatility over past week
- `total_power_kw_rolling_min_168h` - Minimum load over past week
- `total_power_kw_rolling_max_168h` - Peak load over past week

**Rationale**: Rolling statistics smooth out noise and capture longer-term trends.

### 3. Calendar Features
Discrete temporal markers:
- `hour_of_day` - Hour (0-23)
- `day_of_week` - Weekday (0=Monday, 6=Sunday)
- `day_of_month` - Day (1-31)
- `day_of_year` - Day (1-365)
- `week_of_year` - Week (1-52)
- `month` - Month (1-12)
- `quarter` - Quarter (1-4)
- `season` - Season (0=Winter, 1=Spring, 2=Summer, 3=Fall)
- `is_weekend` - Weekend flag (0/1)
- `is_business_hours` - Business hours flag (7am-7pm weekdays)
- `is_peak_hours` - Peak hours flag (6pm-10pm)

**Rationale**: Load patterns vary by time of day, day of week, and season.

### 4. Cyclical Encoding
Preserves circular nature of time using sine/cosine transformation:
- `hour_sin`, `hour_cos` - Hour encoding (hour 23 is close to hour 0)
- `day_sin`, `day_cos` - Day of week encoding
- `month_sin`, `month_cos` - Month encoding
- `day_of_year_sin`, `day_of_year_cos` - Day of year encoding

**Rationale**: Prevents models from treating time as linear (e.g., hour 0 and hour 23 are adjacent).

### 5. Interaction Features
Captures non-linear relationships:
- `hour_season_interaction` - Different hourly patterns by season
- `weekend_hour_interaction` - Different hourly patterns on weekends

**Rationale**: Load patterns differ by context (e.g., weekend mornings vs weekday mornings).

### 6. Power-Derived Features
Domain-specific features:
- `total_sub_metering` - Sum of all sub-metering
- `sub1_pct`, `sub2_pct`, `sub3_pct` - Percentage breakdown by sub-meter
- `power_change_1h` - Hourly rate of change
- `power_change_24h` - Daily rate of change
- `power_acceleration` - Second derivative (change in rate of change)

**Rationale**: Rate of change and sub-metering patterns provide additional predictive signal.

## Usage

### Basic Usage

```bash
# Run feature engineering on Phase 2 output
python features/engineer.py --input data/processed/household_power_hourly.parquet --output data/processed/household_power_features.parquet
```

### Advanced Options

```bash
# Custom lag periods (1h, 6h, 12h, 24h, 48h, 168h)
python features/engineer.py --lag-hours 1 6 12 24 48 168

# Custom rolling windows (12h, 24h, 72h, 168h)
python features/engineer.py --rolling-windows 12 24 72 168

# Skip cyclical encoding (if using models that don't benefit from it)
python features/engineer.py --skip-cyclical

# Show detailed feature information
python features/engineer.py --show-info
```

### Python API

```python
from features.engineer import FeatureEngineer
import pandas as pd

# Load hourly data
df = pd.read_parquet('data/processed/household_power_hourly.parquet')

# Initialize engineer
engineer = FeatureEngineer(
    lag_hours=[1, 24, 168],
    rolling_windows=[24, 168],
    include_calendar=True,
    include_cyclical=True
)

# Transform data
df_features = engineer.fit_transform(df)

# Get feature info
info = engineer.get_feature_info(df_features)
print(info)
```

## Output

### File Format
- **Format**: Apache Parquet (columnar storage)
- **Compression**: Snappy
- **Index**: DatetimeIndex (hourly timestamps)
- **Size**: ~2-3 MB (depending on feature count)

### Expected Features
- **Input columns**: ~13 (from Phase 2 ETL)
- **New features**: ~40-50 (depending on configuration)
- **Total columns**: ~50-60

### Data Quality
- NaN values from lag features (initial rows) are automatically dropped
- All features are numeric (ready for ML models)
- No missing values in final output
- Sorted by datetime

## Feature Engineering Strategy

### Time Series Best Practices

1. **No Data Leakage**: All features use only past data (no future peeking)
2. **Proper Windowing**: Rolling statistics use `min_periods=1` to avoid excessive NaN
3. **Sorted Data**: Datetime index is sorted before feature creation
4. **Missing Value Handling**: Lag-induced NaN values are dropped after all features are created

### Model Compatibility

**Good for**:
- Linear Regression (baseline)
- Random Forest (handles non-linear relationships)
- Gradient Boosting (XGBoost, LightGBM)
- Neural Networks (MLP, LSTM)

**Feature Selection Recommendations**:
- **Tree-based models**: All features (can handle redundancy)
- **Linear models**: Consider feature selection or regularization
- **Neural networks**: Normalize/standardize features first

## Architecture

```
Input: household_power_hourly.parquet (Phase 2)
  ↓
FeatureEngineer.fit_transform()
  ├── Lag Features (autoregressive)
  ├── Rolling Statistics (trend/volatility)
  ├── Calendar Features (temporal markers)
  ├── Cyclical Encoding (sine/cosine)
  ├── Interaction Features (non-linear)
  └── Power-Derived Features (domain-specific)
  ↓
Output: household_power_features.parquet (Phase 3)
  ↓
Ready for Phase 4: Model Training
```

## Performance

- **Processing Time**: ~5-10 seconds for 35K records
- **Memory Usage**: ~50-100 MB peak
- **Output Size**: ~2-3 MB (compressed Parquet)

## Next Steps

After feature engineering, proceed to:

**Phase 4: Model Training**
```bash
# Train models with engineered features
python training/train_models.py --input data/processed/household_power_features.parquet
```

## Troubleshooting

### Issue: "Input file not found"
**Solution**: Run Phase 2 ETL first:
```bash
python ingestion/etl.py --input data/raw/household_power.zip --skip-db
```

### Issue: "All values are NaN"
**Cause**: Insufficient data for lag/rolling features
**Solution**: Ensure input has at least 168 hours (1 week) of data

### Issue: "Memory error"
**Cause**: Large dataset with many rolling windows
**Solution**: Reduce rolling window sizes or process in chunks

## References

- **Time Series Forecasting**: Hyndman & Athanasopoulos, "Forecasting: Principles and Practice"
- **Feature Engineering**: Zheng & Casari, "Feature Engineering for Machine Learning"
- **Load Forecasting**: Hong et al., "Probabilistic Electric Load Forecasting"

## Version

- **Module Version**: 0.1.0
- **Phase**: 3 (Feature Engineering)
- **Dependencies**: pandas, numpy
