"""
Data Quality Validation using Pydantic

This script defines schemas (rules) for what valid data looks like.
Think of it like a checklist that every data record must pass.

Pydantic is a Python library that:
1. Validates data automatically
2. Converts types (e.g., "123" string → 123 integer)
3. Provides clear error messages
4. Documents expected data structure

Example:
    A measurement must have:
    - timestamp (valid datetime)
    - power (positive number, < 20 kW)
    - voltage (between 200-260 V)
    
    If any rule breaks, pydantic tells you exactly what's wrong!
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PowerMeasurement(BaseModel):
    """
    Schema for a single hourly power measurement.
    
    This defines the "contract" - what fields must exist and what values are valid.
    """
    
    # Timestamp
    timestamp: datetime = Field(
        ...,  # ... means required
        description="Measurement timestamp (hourly intervals)"
    )
    
    # Power measurements
    global_active_power: float = Field(
        ge=0.0,  # ge = greater than or equal to
        le=20.0,  # le = less than or equal to
        description="Household global active power (kW)"
    )
    
    global_reactive_power: float = Field(
        ge=0.0,
        le=5.0,
        description="Household global reactive power (kVAr)"
    )
    
    voltage: float = Field(
        ge=200.0,
        le=260.0,
        description="Average voltage (V)"
    )
    
    global_intensity: float = Field(
        ge=0.0,
        le=100.0,
        description="Household global current intensity (A)"
    )
    
    # Sub-metering (energy consumption by area)
    sub_metering_1: float = Field(
        ge=0.0,
        description="Kitchen energy consumption (Wh)"
    )
    
    sub_metering_2: float = Field(
        ge=0.0,
        description="Laundry room energy consumption (Wh)"
    )
    
    sub_metering_3: float = Field(
        ge=0.0,
        description="Water heater & AC energy consumption (Wh)"
    )
    
    # Quality flag
    quality_flag: Literal["OK", "DEGRADED", "MISSING_DATA", "SUSPICIOUS_VOLTAGE"] = Field(
        default="OK",
        description="Data quality indicator"
    )
    
    # Derived features
    hour_of_day: int = Field(
        ge=0,
        le=23,
        description="Hour of day (0-23)"
    )
    
    day_of_week: int = Field(
        ge=0,
        le=6,
        description="Day of week (0=Monday, 6=Sunday)"
    )
    
    month: int = Field(
        ge=1,
        le=12,
        description="Month (1-12)"
    )
    
    is_weekend: int = Field(
        ge=0,
        le=1,
        description="Is weekend? (0=no, 1=yes)"
    )
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp_range(cls, v: datetime) -> datetime:
        """
        Custom validator: ensure timestamp is within expected range.
        
        The UCI dataset covers 2006-2010, so we allow a buffer.
        """
        min_date = datetime(2006, 1, 1)
        max_date = datetime(2011, 12, 31)
        
        if v < min_date or v > max_date:
            raise ValueError(
                f"Timestamp {v} outside expected range ({min_date} to {max_date})"
            )
        
        return v
    
    @field_validator('quality_flag')
    @classmethod
    def validate_quality_flag(cls, v: str) -> str:
        """Ensure quality flag is one of allowed values"""
        allowed = {"OK", "DEGRADED", "MISSING_DATA", "SUSPICIOUS_VOLTAGE"}
        if v not in allowed:
            raise ValueError(f"Invalid quality flag '{v}'. Must be one of: {allowed}")
        return v
    
    class Config:
        # Configuration for pydantic model
        json_schema_extra = {
            "example": {
                "timestamp": "2006-12-16T17:00:00",
                "global_active_power": 4.216,
                "global_reactive_power": 0.418,
                "voltage": 234.84,
                "global_intensity": 18.4,
                "sub_metering_1": 1000.0,
                "sub_metering_2": 1000.0,
                "sub_metering_3": 17000.0,
                "quality_flag": "OK",
                "hour_of_day": 17,
                "day_of_week": 5,
                "month": 12,
                "is_weekend": 1
            }
        }


class DataQualityReport(BaseModel):
    """
    Summary of data quality validation results.
    """
    total_records: int = Field(description="Total number of records validated")
    valid_records: int = Field(description="Number of records that passed validation")
    invalid_records: int = Field(description="Number of records that failed validation")
    error_summary: dict[str, int] = Field(
        default_factory=dict,
        description="Count of each type of validation error"
    )
    
    @property
    def success_rate(self) -> float:
        """Calculate percentage of valid records"""
        if self.total_records == 0:
            return 0.0
        return (self.valid_records / self.total_records) * 100


def validate_dataframe(df) -> DataQualityReport:
    """
    Validate a pandas DataFrame against the PowerMeasurement schema.
    
    This function:
    1. Converts each row to a dictionary
    2. Tries to create a PowerMeasurement object from it
    3. If validation fails, logs the error
    4. Returns a summary report
    
    Args:
        df: pandas DataFrame with power measurements
        
    Returns:
        DataQualityReport with validation results
    """
    import logging
    from pydantic import ValidationError
    
    logger = logging.getLogger(__name__)
    
    valid_count = 0
    invalid_count = 0
    error_counts = {}
    
    logger.info(f"Validating {len(df)} records...")
    
    for idx, row in df.iterrows():
        try:
            # Convert row to dict and validate
            record_dict = row.to_dict()
            record_dict['timestamp'] = idx  # Add timestamp from index
            
            # This will raise ValidationError if data is invalid
            PowerMeasurement(**record_dict)
            valid_count += 1
            
        except ValidationError as e:
            invalid_count += 1
            
            # Count types of errors
            for error in e.errors():
                error_type = error['type']
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            # Log first few errors in detail
            if invalid_count <= 5:
                logger.warning(f"Validation error at index {idx}: {e}")
    
    report = DataQualityReport(
        total_records=len(df),
        valid_records=valid_count,
        invalid_records=invalid_count,
        error_summary=error_counts
    )
    
    logger.info("=" * 60)
    logger.info("Data Quality Report")
    logger.info("=" * 60)
    logger.info(f"Total records:   {report.total_records:,}")
    logger.info(f"Valid records:   {report.valid_records:,}")
    logger.info(f"Invalid records: {report.invalid_records:,}")
    logger.info(f"Success rate:    {report.success_rate:.2f}%")
    
    if report.error_summary:
        logger.info("\nError breakdown:")
        for error_type, count in sorted(report.error_summary.items(), key=lambda x: -x[1]):
            logger.info(f"  {error_type}: {count:,}")
    
    logger.info("=" * 60)
    
    return report


# Example usage
if __name__ == "__main__":
    """
    Demonstrate how to use the validation schema.
    """
    
    # Example 1: Valid measurement
    valid_measurement = {
        "timestamp": datetime(2006, 12, 16, 17, 0, 0),
        "global_active_power": 4.216,
        "global_reactive_power": 0.418,
        "voltage": 234.84,
        "global_intensity": 18.4,
        "sub_metering_1": 1000.0,
        "sub_metering_2": 1000.0,
        "sub_metering_3": 17000.0,
        "quality_flag": "OK",
        "hour_of_day": 17,
        "day_of_week": 5,
        "month": 12,
        "is_weekend": 1
    }
    
    try:
        measurement = PowerMeasurement(**valid_measurement)
        print("✓ Valid measurement created:")
        print(measurement.model_dump_json(indent=2))
    except Exception as e:
        print(f"✗ Validation failed: {e}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Example 2: Invalid measurement (voltage too high)
    invalid_measurement = {
        **valid_measurement,
        "voltage": 300.0  # Too high! Should be 200-260V
    }
    
    try:
        measurement = PowerMeasurement(**invalid_measurement)
        print("✓ Valid measurement created")
    except Exception as e:
        print(f"✗ Validation failed (expected):")
        print(f"   {e}")
