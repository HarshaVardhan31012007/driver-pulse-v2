"""
Configuration Module for Driver Pulse
Centralizes all configuration parameters and settings.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json


class DriverPulseConfig:
    """Central configuration class for Driver Pulse system."""
    
    # Project Metadata
    NAME = "Driver Pulse"
    VERSION = "1.0.0"
    DESCRIPTION = "Driver safety and earnings analytics platform"
    AUTHOR = "Team Velocity"
    CREATED_DATE = "2024-03-10"
    
    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_ROOT = PROJECT_ROOT / "data"
    RAW_DATA_PATH = DATA_ROOT / "raw"
    PROCESSED_DATA_PATH = DATA_ROOT / "processed"
    OUTPUTS_PATH = PROJECT_ROOT / "outputs"
    LOGS_PATH = PROJECT_ROOT / "logs"
    
    # Application Settings
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "10000"))
    
    # Dashboard Settings
    DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
    DASHBOARD_TITLE = f"{NAME} Analytics Dashboard"
    
    # Legacy paths (for backward compatibility)
    DATA_DIR = "./data"
    OUTPUT_DIR = "./outputs"
    SAMPLE_DATA_DIR = "./data/sample_data"
    
    # Accelerometer thresholds (in g-force)
    ACCEL_THRESHOLDS = {
        'HARSH_BRAKE_THRESHOLD': -2.0,
        'HARSH_ACCEL_THRESHOLD': 2.0,
        'MODERATE_BRAKE_THRESHOLD': -1.5,
        'MODERATE_ACCEL_THRESHOLD': 1.5,
        'EXTREME_ACCEL_THRESHOLD': 3.0
    }
    
    # Audio thresholds (in dB)
    AUDIO_THRESHOLDS = {
        'NOISE_SPIKE_THRESHOLD': 80,
        'SUSTAINED_HIGH_THRESHOLD': 70,
        'EXTREME_NOISE_THRESHOLD': 90,
        'NORMAL_NOISE_THRESHOLD': 60
    }
    
    # Signal processing parameters
    SIGNAL_PROCESSING = {
        'SAMPLING_RATE': 10,  # Hz
        'ROLLING_WINDOW_SIZE': 5,  # samples
        'MIN_EVENT_DURATION': 0.5,  # seconds
        'SAVITZKY_GOLAY_WINDOW': 11,  # samples
        'SAVITZKY_GOLAY_POLYORDER': 3
    }
    
    # Event fusion parameters
    FUSION_PARAMETERS = {
        'COINCIDENCE_WINDOW_SECONDS': 5.0,
        'MIN_FUSION_CONFIDENCE': 0.5,
        'SIGNAL_WEIGHTS': {
            'accelerometer': 0.6,
            'audio': 0.4
        },
        'HIGH_STRESS_THRESHOLD': 0.8,
        'MEDIUM_STRESS_THRESHOLD': 0.6
    }
    
    # Audio event parameters
    AUDIO_EVENT_PARAMS = {
        'SUSTAINED_DURATION_MIN': 3.0,  # seconds
        'SPIKE_WINDOW_SIZE': 1.0,  # seconds
        'SPIKE_THRESHOLD_DB': 10,  # dB increase
        'EXPONENTIAL_SMOOTHING_ALPHA': 0.3
    }
    
    # Earnings velocity parameters
    EARNINGS_VELOCITY = {
        'MIN_HOURS_FOR_VELOCITY': 2.0,
        'VELOCITY_WINDOW_HOURS': 4.0,
        'COLD_START_VELOCITY': 15.0,  # $/hour
        'FORECAST_HORIZON_HOURS': 8.0,
        'MIN_DATA_POINTS': 5,
        'TIME_BIN_MINUTES': 15  # minutes for earnings aggregation
    }
    
    # Goal prediction parameters
    GOAL_PREDICTION = {
        'ON_TRACK_THRESHOLD': 0.8,
        'AT_RISK_THRESHOLD': 0.5,
        'MIN_HOURS_FOR_PREDICTION': 1.0,
        'PEAK_HOURS_MULTIPLIER': 1.3,
        'OFF_PEAK_HOURS_MULTIPLIER': 0.8,
        'COLD_START_PROGRESS_RATE': 0.15,
        'TYPICAL_DAILY_HOURS': 8.0,
        'WORKDAY_END_HOUR': 22  # 10 PM
    }
    
    # Trip summary parameters
    TRIP_SUMMARY = {
        'STRESS_WEIGHTS': {
            'critical_stress': 10.0,
            'high_stress': 7.0,
            'medium_stress': 4.0,
            'low_stress': 2.0,
            'harsh_braking': 3.0,
            'harsh_acceleration': 2.5,
            'moderate_braking': 1.5,
            'moderate_acceleration': 1.0,
            'extreme_noise': 4.0,
            'noise_spike': 2.0,
            'sustained_high_noise': 1.5
        },
        'EARNINGS_PER_MINUTE_RANGE': {
            'min': 0.5,
            'max': 2.0
        }
    }
    
    # Dashboard settings
    DASHBOARD = {
        'PAGE_TITLE': 'Driver Pulse Dashboard',
        'LAYOUT': 'wide',
        'REFRESH_INTERVAL': 30,  # seconds
        'MAX_CHART_POINTS': 1000,
        'DEFAULT_TIME_RANGE': '24h'
    }
    
    # Logging settings
    LOGGING = {
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'MAX_LOG_SIZE_MB': 10,
        'BACKUP_COUNT': 5
    }
    
    # Export settings
    EXPORT = {
        'DEFAULT_FORMAT': 'csv',
        'SUPPORTED_FORMATS': ['csv', 'json', 'parquet'],
        'INCLUDE_TIMESTAMP_IN_FILENAME': True
    }
    
    # Performance settings
    PERFORMANCE = {
        'MAX_MEMORY_USAGE_MB': 500,
        'CHUNK_SIZE': 10000,  # for processing large datasets
        'PARALLEL_PROCESSING': True,
        'MAX_WORKERS': 4
    }
    
    @classmethod
    def get_accelerometer_thresholds(cls) -> Dict[str, float]:
        """Get accelerometer thresholds."""
        return cls.ACCEL_THRESHOLDS.copy()
    
    @classmethod
    def get_audio_thresholds(cls) -> Dict[str, float]:
        """Get audio thresholds."""
        return cls.AUDIO_THRESHOLDS.copy()
    
    @classmethod
    def get_fusion_parameters(cls) -> Dict:
        """Get fusion parameters."""
        return cls.FUSION_PARAMETERS.copy()
    
    @classmethod
    def get_earnings_velocity_params(cls) -> Dict:
        """Get earnings velocity parameters."""
        return cls.EARNINGS_VELOCITY.copy()
    
    @classmethod
    def get_goal_prediction_params(cls) -> Dict:
        """Get goal prediction parameters."""
        return cls.GOAL_PREDICTION.copy()
    
    @classmethod
    def validate_paths(cls) -> bool:
        """Validate that all required paths exist or can be created."""
        paths_to_check = [
            cls.DATA_DIR,
            cls.OUTPUT_DIR,
            cls.SAMPLE_DATA_DIR
        ]
        
        for path in paths_to_check:
            if not os.path.exists(path):
                try:
                    os.makedirs(path, exist_ok=True)
                except Exception as e:
                    print(f"Error creating directory {path}: {e}")
                    return False
        
        return True
    
    @classmethod
    def get_peak_hours(cls) -> Dict[str, List[int]]:
        """Get peak hour definitions."""
        return {
            'weekday_morning': list(range(7, 10)),  # 7-9 AM
            'weekday_evening': list(range(17, 20)),  # 5-7 PM
            'weekend': list(range(10, 23))  # 10 AM - 10 PM
        }
    
    @classmethod
    def is_peak_hour(cls, hour: int, day_of_week: int) -> bool:
        """Check if given hour is peak hour for the day."""
        peak_hours = cls.get_peak_hours()
        
        if day_of_week < 5:  # Monday-Friday
            return (hour in peak_hours['weekday_morning'] or 
                   hour in peak_hours['weekday_evening'])
        else:  # Weekend
            return hour in peak_hours['weekend']
    
    @classmethod
    def get_safety_rating_criteria(cls) -> Dict[str, Dict]:
        """Get safety rating criteria."""
        return {
            'EXCELLENT': {
                'max_stress_score': 1.0,
                'max_events': 2,
                'description': 'Excellent safety performance'
            },
            'GOOD': {
                'max_stress_score': 2.5,
                'max_events': 5,
                'description': 'Good safety performance'
            },
            'FAIR': {
                'max_stress_score': 5.0,
                'max_events': 10,
                'description': 'Fair safety performance'
            },
            'POOR': {
                'max_stress_score': 8.0,
                'max_events': 20,
                'description': 'Poor safety performance'
            },
            'CRITICAL': {
                'max_stress_score': float('inf'),
                'max_events': float('inf'),
                'description': 'Critical safety issues'
            }
        }
    
    @classmethod
    def get_event_combination_rules(cls) -> Dict[str, str]:
        """Get event combination rules for fusion."""
        return {
            'harsh_braking + noise_spike': 'high_stress',
            'harsh_acceleration + noise_spike': 'high_stress',
            'harsh_braking + sustained_high_noise': 'high_stress',
            'harsh_acceleration + sustained_high_noise': 'medium_stress',
            'moderate_braking + noise_spike': 'medium_stress',
            'moderate_acceleration + noise_spike': 'medium_stress',
            'extreme_noise + harsh_braking': 'critical_stress',
            'extreme_noise + harsh_acceleration': 'critical_stress'
        }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        directories = [
            cls.DATA_ROOT,
            cls.RAW_DATA_PATH,
            cls.PROCESSED_DATA_PATH,
            cls.OUTPUTS_PATH,
            cls.LOGS_PATH,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_log_file_path(cls, log_name: str) -> Path:
        """Get path for a log file."""
        timestamp = datetime.now().strftime("%Y%m%d")
        return cls.LOGS_PATH / f"{log_name}_{timestamp}.log"
    
    @classmethod
    def get_output_file_path(cls, filename: str) -> Path:
        """Get path for an output file."""
        return cls.OUTPUTS_PATH / f"{filename}.csv"
    
    @classmethod
    def get_raw_data_path(cls, filename: str) -> Path:
        """Get path for a raw data file."""
        return cls.RAW_DATA_PATH / f"{filename}.csv"
    
    @classmethod
    def get_processed_data_path(cls, filename: str) -> Path:
        """Get path for a processed data file."""
        return cls.PROCESSED_DATA_PATH / f"{filename}.csv"
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary."""
        return {
            "project": {
                "name": cls.NAME,
                "version": cls.VERSION,
                "description": cls.DESCRIPTION,
                "author": cls.AUTHOR,
                "created_date": cls.CREATED_DATE,
            },
            "paths": {
                "project_root": str(cls.PROJECT_ROOT),
                "data_root": str(cls.DATA_ROOT),
                "outputs_path": str(cls.OUTPUTS_PATH),
                "logs_path": str(cls.LOGS_PATH),
            },
            "settings": {
                "debug": cls.DEBUG,
                "log_level": cls.LOG_LEVEL,
                "max_workers": cls.MAX_WORKERS,
                "chunk_size": cls.CHUNK_SIZE,
            },
            "dashboard": {
                "host": cls.DASHBOARD_HOST,
                "port": cls.DASHBOARD_PORT,
                "title": cls.DASHBOARD_TITLE,
            }
        }
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all required directories exist."""
        directories = [
            cls.DATA_ROOT,
            cls.RAW_DATA_PATH,
            cls.PROCESSED_DATA_PATH,
            cls.OUTPUTS_PATH,
            cls.LOGS_PATH,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_log_file_path(cls, log_name: str) -> Path:
        """Get path for a log file."""
        timestamp = datetime.now().strftime("%Y%m%d")
        return cls.LOGS_PATH / f"{log_name}_{timestamp}.log"
    
    @classmethod
    def get_output_file_path(cls, filename: str) -> Path:
        """Get path for an output file."""
        return cls.OUTPUTS_PATH / f"{filename}.csv"
    
    @classmethod
    def get_raw_data_path(cls, filename: str) -> Path:
        """Get path for a raw data file."""
        return cls.RAW_DATA_PATH / f"{filename}.csv"
    
    @classmethod
    def get_processed_data_path(cls, filename: str) -> Path:
        """Get path for a processed data file."""
        return cls.PROCESSED_DATA_PATH / f"{filename}.csv"
    
    @classmethod
    def to_dict(cls) -> dict:
        """Convert configuration to dictionary."""
        return {
            "project": {
                "name": cls.NAME,
                "version": cls.VERSION,
                "description": cls.DESCRIPTION,
                "author": cls.AUTHOR,
                "created_date": cls.CREATED_DATE,
            },
            "paths": {
                "project_root": str(cls.PROJECT_ROOT),
                "data_root": str(cls.DATA_ROOT),
                "outputs_path": str(cls.OUTPUTS_PATH),
                "logs_path": str(cls.LOGS_PATH),
            },
            "settings": {
                "debug": cls.DEBUG,
                "log_level": cls.LOG_LEVEL,
                "max_workers": cls.MAX_WORKERS,
                "chunk_size": cls.CHUNK_SIZE,
            },
            "dashboard": {
                "host": cls.DASHBOARD_HOST,
                "port": cls.DASHBOARD_PORT,
                "title": cls.DASHBOARD_TITLE,
            }
        }
    
# Environment-specific configurations
class DevelopmentConfig(DriverPulseConfig):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_METRICS = False


class ProductionConfig(DriverPulseConfig):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    ENABLE_METRICS = True
    MEMORY_LIMIT_GB = 8


class TestingConfig(DriverPulseConfig):
    """Testing environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    ENABLE_METRICS = False
    CHUNK_SIZE = 100  # Smaller chunks for testing


def get_config() -> DriverPulseConfig:
    """Get appropriate configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()


# Global configuration instance
config = get_config()

# Ensure directories exist when module is imported
config.ensure_directories()
