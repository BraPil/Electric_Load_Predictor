"""
Feature Validation and Visualization

This script validates the feature engineering output and provides
insights into the created features.

Usage:
    python scripts/validate_features.py
"""

import pandas as pd
import numpy as np
from pathlib import Path


def main():
    """Validate and analyze engineered features."""
    
    print("="*80)
    print("FEATURE VALIDATION & ANALYSIS")
    print("="*80)
    
    # Load features
    features_path = Path('data/processed/household_power_features.parquet')
    
    if not features_path.exists():
        print("\nERROR: Feature file not found!")
        print("Run: python features/engineer.py")
        return
    
    print(f"\nLoading features from: {features_path}")
    df = pd.read_parquet(features_path)
    
    print(f"\nDATASET OVERVIEW")
    print(f"   Records: {len(df):,}")
    print(f"   Features: {len(df.columns)}")
    print(f"   Date Range: {df.index.min()} to {df.index.max()}")
    print(f"   Duration: {(df.index.max() - df.index.min()).days} days")
    
    # Feature categories (only select numeric columns)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    lag_features = [col for col in numeric_cols if '_lag_' in col]
    rolling_features = [col for col in numeric_cols if 'rolling' in col]
    calendar_features = [col for col in numeric_cols if any(x in col for x in ['hour', 'day', 'month', 'week', 'season', 'quarter'])]
    cyclical_features = [col for col in numeric_cols if any(x in col for x in ['sin', 'cos'])]
    power_features = [col for col in numeric_cols if 'power' in col or 'metering' in col]
    
    print(f"\nFEATURE CATEGORIES")
    print(f"   Lag Features: {len(lag_features)}")
    print(f"   Rolling Features: {len(rolling_features)}")
    print(f"   Calendar Features: {len(calendar_features)}")
    print(f"   Cyclical Features: {len(cyclical_features)}")
    print(f"   Power Features: {len(power_features)}")
    
    # Check for missing values
    missing = df.isna().sum()
    if missing.sum() == 0:
        print(f"\n[OK] DATA QUALITY: No missing values")
    else:
        print(f"\n[WARNING] {missing.sum()} missing values found")
        print(missing[missing > 0])
    
    # Lag feature validation
    print(f"\nLAG FEATURES")
    for col in lag_features:
        print(f"   {col}: mean={df[col].mean():.3f}, std={df[col].std():.3f}")
    
    # Rolling feature statistics
    print(f"\nROLLING FEATURES (sample)")
    for col in rolling_features[:4]:
        print(f"   {col}: mean={df[col].mean():.3f}, std={df[col].std():.3f}")
    
    # Calendar feature distribution
    print(f"\nCALENDAR FEATURES")
    print(f"   Weekday records: {(df['is_weekend'] == 0).sum():,} ({(df['is_weekend'] == 0).sum() / len(df) * 100:.1f}%)")
    print(f"   Weekend records: {(df['is_weekend'] == 1).sum():,} ({(df['is_weekend'] == 1).sum() / len(df) * 100:.1f}%)")
    print(f"   Business hours: {(df['is_business_hours'] == 1).sum():,} ({(df['is_business_hours'] == 1).sum() / len(df) * 100:.1f}%)")
    print(f"   Peak hours: {(df['is_peak_hours'] == 1).sum():,} ({(df['is_peak_hours'] == 1).sum() / len(df) * 100:.1f}%)")
    
    # Cyclical encoding validation
    print(f"\nCYCLICAL ENCODING VALIDATION")
    print(f"   hour_sin range: [{df['hour_sin'].min():.3f}, {df['hour_sin'].max():.3f}]")
    print(f"   hour_cos range: [{df['hour_cos'].min():.3f}, {df['hour_cos'].max():.3f}]")
    # Verify circular property: sin^2 + cos^2 = 1
    circular_check = df['hour_sin']**2 + df['hour_cos']**2
    print(f"   Circular property (sin²+cos²): mean={circular_check.mean():.6f} (should be ~1.0)")
    
    # Power feature insights
    print(f"\nPOWER CONSUMPTION INSIGHTS")
    print(f"   Average power: {df['total_power_kw'].mean():.3f} kW")
    print(f"   Peak power: {df['total_power_kw'].max():.3f} kW")
    print(f"   Min power: {df['total_power_kw'].min():.3f} kW")
    print(f"   Std dev: {df['total_power_kw'].std():.3f} kW")
    
    # Sample data display
    print(f"\nSAMPLE FEATURES (first 5 records)")
    sample_cols = ['total_power_kw', 'total_power_kw_lag_24h', 
                   'total_power_kw_rolling_mean_24h', 'hour_of_day', 
                   'day_of_week', 'is_weekend']
    print(df[sample_cols].head().to_string())
    
    # Correlation analysis (top features with target)
    print(f"\nTOP 10 FEATURES CORRELATED WITH POWER CONSUMPTION")
    numeric_df = df.select_dtypes(include=[np.number])
    correlations = numeric_df.corr()['total_power_kw'].abs().sort_values(ascending=False)
    print(correlations.head(11).to_string())  # Top 11 (includes itself)
    
    # Feature importance proxy (variance)
    print(f"\nHIGH-VARIANCE FEATURES (top 10)")
    variances = numeric_df.var().sort_values(ascending=False)
    print(variances.head(10).to_string())
    
    # File size
    file_size_mb = features_path.stat().st_size / (1024 * 1024)
    print(f"\nFILE SIZE: {file_size_mb:.2f} MB")
    
    print("\n" + "="*80)
    print("[OK] FEATURE VALIDATION COMPLETE")
    print("="*80)
    print("\nFeatures are ready for model training (Phase 4)")
    print("\nNext step:")
    print("   python training/train_models.py --input data/processed/household_power_features.parquet")
    print("="*80)


if __name__ == '__main__':
    main()
