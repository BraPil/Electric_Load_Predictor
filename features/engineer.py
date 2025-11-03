"""
Feature Engineering Pipeline for Electric Load Prediction

This module transforms hourly power consumption data into ML-ready features including:
- Lag features (1h, 24h, 168h lookback)
- Rolling statistics (24h and 168h windows)
- Seasonal patterns (hour, day, month, season)
- Calendar features (holidays, weekends, business hours)

Usage:
    python features/engineer.py --input data/processed/household_power_hourly.parquet --output data/processed/household_power_features.parquet

Architecture:
    Input: Hourly power consumption data (from Phase 2 ETL)
    Output: Feature-enriched dataset ready for model training
    Mode: File-only (Parquet) or Database mode
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List

import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering for time series electric load prediction.
    
    Creates temporal, statistical, and domain-specific features to improve
    model performance for load forecasting.
    """
    
    def __init__(
        self,
        lag_hours: List[int] = None,
        rolling_windows: List[int] = None,
        include_calendar: bool = True,
        include_cyclical: bool = True
    ):
        """
        Initialize feature engineer.
        
        Args:
            lag_hours: List of lag periods in hours (default: [1, 24, 168])
            rolling_windows: List of rolling window sizes in hours (default: [24, 168])
            include_calendar: Whether to include calendar features (default: True)
            include_cyclical: Whether to include cyclical encoding (default: True)
        """
        self.lag_hours = lag_hours or [1, 24, 168]  # 1h, 1 day, 1 week
        self.rolling_windows = rolling_windows or [24, 168]  # 1 day, 1 week
        self.include_calendar = include_calendar
        self.include_cyclical = include_cyclical
        
        logger.info(f"FeatureEngineer initialized with {len(self.lag_hours)} lag features, "
                   f"{len(self.rolling_windows)} rolling windows")
    
    def create_lag_features(self, df: pd.DataFrame, target_col: str = 'total_power_kw') -> pd.DataFrame:
        """
        Create lag features for the target variable.
        
        Args:
            df: Input dataframe with datetime index
            target_col: Column to create lags for
            
        Returns:
            DataFrame with added lag features
        """
        logger.info(f"Creating {len(self.lag_hours)} lag features for '{target_col}'")
        
        for lag in self.lag_hours:
            col_name = f'{target_col}_lag_{lag}h'
            df[col_name] = df[target_col].shift(lag)
            
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, target_col: str = 'total_power_kw') -> pd.DataFrame:
        """
        Create rolling window statistics.
        
        Args:
            df: Input dataframe with datetime index
            target_col: Column to compute statistics for
            
        Returns:
            DataFrame with added rolling features
        """
        logger.info(f"Creating rolling features for {len(self.rolling_windows)} windows")
        
        for window in self.rolling_windows:
            # Rolling mean
            df[f'{target_col}_rolling_mean_{window}h'] = (
                df[target_col].rolling(window=window, min_periods=1).mean()
            )
            
            # Rolling std
            df[f'{target_col}_rolling_std_{window}h'] = (
                df[target_col].rolling(window=window, min_periods=1).std()
            )
            
            # Rolling min
            df[f'{target_col}_rolling_min_{window}h'] = (
                df[target_col].rolling(window=window, min_periods=1).min()
            )
            
            # Rolling max
            df[f'{target_col}_rolling_max_{window}h'] = (
                df[target_col].rolling(window=window, min_periods=1).max()
            )
            
        return df
    
    def create_calendar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create calendar-based features.
        
        Args:
            df: Input dataframe with datetime index
            
        Returns:
            DataFrame with added calendar features
        """
        if not self.include_calendar:
            return df
            
        logger.info("Creating calendar features")
        
        # These may already exist from ETL, but we'll ensure they're present
        if 'hour_of_day' not in df.columns:
            df['hour_of_day'] = df.index.hour
        if 'day_of_week' not in df.columns:
            df['day_of_week'] = df.index.dayofweek
        if 'month' not in df.columns:
            df['month'] = df.index.month
        if 'is_weekend' not in df.columns:
            df['is_weekend'] = df.index.dayofweek.isin([5, 6]).astype(int)
        
        # Additional calendar features
        df['day_of_month'] = df.index.day
        df['day_of_year'] = df.index.dayofyear
        df['week_of_year'] = df.index.isocalendar().week
        df['quarter'] = df.index.quarter
        
        # Business hours (7am-7pm on weekdays)
        df['is_business_hours'] = (
            (df.index.hour >= 7) & 
            (df.index.hour < 19) & 
            (df.index.dayofweek < 5)
        ).astype(int)
        
        # Peak hours (typically 6pm-10pm)
        df['is_peak_hours'] = (
            (df.index.hour >= 18) & (df.index.hour < 22)
        ).astype(int)
        
        # Season (meteorological seasons)
        df['season'] = df.index.month.map({
            12: 0, 1: 0, 2: 0,  # Winter
            3: 1, 4: 1, 5: 1,   # Spring
            6: 2, 7: 2, 8: 2,   # Summer
            9: 3, 10: 3, 11: 3  # Fall
        })
        
        return df
    
    def create_cyclical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create cyclical encoding for temporal features.
        
        Cyclical encoding preserves the circular nature of time (e.g., hour 23 is close to hour 0).
        Uses sine/cosine transformation.
        
        Args:
            df: Input dataframe with datetime index
            
        Returns:
            DataFrame with added cyclical features
        """
        if not self.include_cyclical:
            return df
            
        logger.info("Creating cyclical features")
        
        # Hour of day (0-23)
        df['hour_sin'] = np.sin(2 * np.pi * df.index.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df.index.hour / 24)
        
        # Day of week (0-6)
        df['day_sin'] = np.sin(2 * np.pi * df.index.dayofweek / 7)
        df['day_cos'] = np.cos(2 * np.pi * df.index.dayofweek / 7)
        
        # Month (1-12)
        df['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
        df['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)
        
        # Day of year (1-365)
        df['day_of_year_sin'] = np.sin(2 * np.pi * df.index.dayofyear / 365)
        df['day_of_year_cos'] = np.cos(2 * np.pi * df.index.dayofyear / 365)
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between important variables.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with added interaction features
        """
        logger.info("Creating interaction features")
        
        # Temperature-like patterns (using hour and season as proxies)
        if 'hour_of_day' in df.columns and 'season' in df.columns:
            df['hour_season_interaction'] = df['hour_of_day'] * df['season']
        
        # Weekend + hour interaction (different patterns on weekends)
        if 'is_weekend' in df.columns and 'hour_of_day' in df.columns:
            df['weekend_hour_interaction'] = df['is_weekend'] * df['hour_of_day']
        
        return df
    
    def create_power_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create features derived from power consumption patterns.
        
        Args:
            df: Input dataframe
            
        Returns:
            DataFrame with added derived features
        """
        logger.info("Creating power-derived features")
        
        # Power intensity (if sub-metering exists)
        if all(col in df.columns for col in ['sub_metering_1', 'sub_metering_2', 'sub_metering_3']):
            df['total_sub_metering'] = (
                df['sub_metering_1'] + df['sub_metering_2'] + df['sub_metering_3']
            )
            
            # Percentage of each sub-meter
            total = df['total_sub_metering'].replace(0, np.nan)
            df['sub1_pct'] = (df['sub_metering_1'] / total * 100).fillna(0)
            df['sub2_pct'] = (df['sub_metering_2'] / total * 100).fillna(0)
            df['sub3_pct'] = (df['sub_metering_3'] / total * 100).fillna(0)
        
        # Power change rate
        if 'total_power_kw' in df.columns:
            df['power_change_1h'] = df['total_power_kw'].diff(1)
            df['power_change_24h'] = df['total_power_kw'].diff(24)
            
            # Power change acceleration
            df['power_acceleration'] = df['power_change_1h'].diff(1)
        
        return df
    
    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps.
        
        Args:
            df: Input dataframe with datetime index
            
        Returns:
            Feature-enriched dataframe
        """
        logger.info(f"Starting feature engineering on {len(df)} records")
        initial_cols = len(df.columns)
        
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'datetime' in df.columns:
                df = df.set_index('datetime')
            else:
                raise ValueError("DataFrame must have datetime index or 'datetime' column")
        
        # Sort by datetime
        df = df.sort_index()
        
        # Apply feature engineering steps
        df = self.create_lag_features(df)
        df = self.create_rolling_features(df)
        df = self.create_calendar_features(df)
        df = self.create_cyclical_features(df)
        df = self.create_interaction_features(df)
        df = self.create_power_derived_features(df)
        
        final_cols = len(df.columns)
        logger.info(f"Feature engineering complete: {initial_cols} -> {final_cols} columns "
                   f"({final_cols - initial_cols} new features)")
        
        return df
    
    def get_feature_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get information about engineered features.
        
        Args:
            df: Feature-enriched dataframe
            
        Returns:
            DataFrame with feature statistics
        """
        feature_info = []
        
        for col in df.columns:
            info = {
                'feature': col,
                'dtype': str(df[col].dtype),
                'missing': df[col].isna().sum(),
                'missing_pct': f"{df[col].isna().sum() / len(df) * 100:.2f}%",
                'unique': df[col].nunique(),
                'mean': df[col].mean() if pd.api.types.is_numeric_dtype(df[col]) else None,
                'std': df[col].std() if pd.api.types.is_numeric_dtype(df[col]) else None,
            }
            feature_info.append(info)
        
        return pd.DataFrame(feature_info)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Feature Engineering for Electric Load Prediction'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data/processed/household_power_hourly.parquet',
        help='Input Parquet file from Phase 2 ETL'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/processed/household_power_features.parquet',
        help='Output Parquet file with engineered features'
    )
    parser.add_argument(
        '--lag-hours',
        type=int,
        nargs='+',
        default=[1, 24, 168],
        help='Lag periods in hours (default: 1 24 168)'
    )
    parser.add_argument(
        '--rolling-windows',
        type=int,
        nargs='+',
        default=[24, 168],
        help='Rolling window sizes in hours (default: 24 168)'
    )
    parser.add_argument(
        '--skip-cyclical',
        action='store_true',
        help='Skip cyclical encoding features'
    )
    parser.add_argument(
        '--show-info',
        action='store_true',
        help='Display feature information after engineering'
    )
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        logger.info("Run Phase 2 ETL first: python ingestion/etl.py --skip-db")
        sys.exit(1)
    
    # Load data
    logger.info(f"Loading data from {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"Loaded {len(df)} records from {df.index.min()} to {df.index.max()}")
    
    # Initialize feature engineer
    engineer = FeatureEngineer(
        lag_hours=args.lag_hours,
        rolling_windows=args.rolling_windows,
        include_cyclical=not args.skip_cyclical
    )
    
    # Engineer features
    df_features = engineer.fit_transform(df)
    
    # Drop rows with NaN values from lag features (initial rows)
    initial_len = len(df_features)
    df_features = df_features.dropna()
    final_len = len(df_features)
    logger.info(f"Dropped {initial_len - final_len} rows with NaN values from lag features")
    
    # Save to Parquet
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving {len(df_features)} records to {output_path}")
    df_features.to_parquet(
        output_path,
        compression='snappy',
        index=True
    )
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    logger.info(f"Successfully saved features: {file_size_mb:.2f} MB")
    
    # Display feature information
    if args.show_info:
        logger.info("\n" + "="*80)
        logger.info("FEATURE INFORMATION")
        logger.info("="*80)
        
        feature_info = engineer.get_feature_info(df_features)
        print(feature_info.to_string(index=False))
        
        logger.info("\n" + "="*80)
        logger.info("FEATURE SUMMARY")
        logger.info("="*80)
        logger.info(f"Total features: {len(df_features.columns)}")
        logger.info(f"Total records: {len(df_features)}")
        logger.info(f"Date range: {df_features.index.min()} to {df_features.index.max()}")
        logger.info(f"Missing values: {df_features.isna().sum().sum()}")
        
    logger.info("\n" + "="*80)
    logger.info("FEATURE ENGINEERING COMPLETE!")
    logger.info("="*80)
    logger.info(f"Output: {output_path}")
    logger.info(f"Records: {len(df_features)}")
    logger.info(f"Features: {len(df_features.columns)}")
    logger.info("\nReady for Phase 4: Model Training")
    logger.info("="*80)


if __name__ == '__main__':
    main()
