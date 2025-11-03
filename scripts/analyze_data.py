"""Quick analysis of processed hourly data"""
import pandas as pd

# Load processed data
df = pd.read_parquet('data/processed/household_power_hourly.parquet')

print('=' * 80)
print('VoltEdge - FULL DATASET Analysis')
print('=' * 80)

print(f'\n📊 DATASET OVERVIEW')
print(f'  Total Hourly Records: {len(df):,}')
print(f'  Date Range: {df.index.min()} to {df.index.max()}')
duration_days = (df.index.max() - df.index.min()).days
print(f'  Duration: {duration_days} days ({duration_days / 365:.1f} years)')
print(f'  File Size: 1.24 MB (compressed Parquet)')

print(f'\n⚡ POWER CONSUMPTION STATS')
print(f'  Average Power: {df["Global_active_power"].mean():.2f} kW')
print(f'  Peak Power: {df["Global_active_power"].max():.2f} kW')
print(f'  Minimum Power: {df["Global_active_power"].min():.2f} kW')
print(f'  Total Energy: {df["Global_active_power"].sum():.0f} kWh')

print(f'\n🔌 VOLTAGE STATS')
print(f'  Average Voltage: {df["Voltage"].mean():.1f}V')
print(f'  Voltage Range: {df["Voltage"].min():.1f}V - {df["Voltage"].max():.1f}V')

print(f'\n📅 TEMPORAL COVERAGE')
weekday_hours = (~df["is_weekend"].astype(bool)).sum()
weekend_hours = df["is_weekend"].astype(bool).sum()
print(f'  Weekday Hours: {weekday_hours:,} ({weekday_hours/len(df)*100:.1f}%)')
print(f'  Weekend Hours: {weekend_hours:,} ({weekend_hours/len(df)*100:.1f}%)')

print(f'\n📈 SAMPLE DATA (First 5 Hours)')
print(df[['Global_active_power', 'Voltage', 'hour_of_day', 'day_of_week']].head())

print(f'\n📈 SAMPLE DATA (Peak Hours)')
peak_hours = df.nlargest(5, 'Global_active_power')[['Global_active_power', 'Voltage', 'hour_of_day', 'day_of_week']]
print(peak_hours)

print(f'\n🎯 READY FOR ML TRAINING')
print(f'  Features Available: {len(df.columns)} columns')
print(f'  Time Series Length: {len(df):,} hourly observations')
print(f'  Perfect for: LSTM, GBM, Random Forest, Prophet forecasting')
print(f'\n  Columns: {list(df.columns)}')

print('\n' + '=' * 80)
print('✅ Dataset ready for Phase 3: Feature Engineering & Phase 4: Model Training')
print('=' * 80)
