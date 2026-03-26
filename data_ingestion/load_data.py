"""
Data Loading Module for Driver Pulse
Handles loading and initial validation of all CSV data sources.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Optional, Tuple
import os


class DataLoader:
    """Handles loading of all driver pulse data sources."""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.required_files = {
            'trips': 'trips/trips.csv',
            'drivers': 'drivers/drivers.csv', 
            'accelerometer': 'sensor_data/accelerometer_data.csv',
            'audio': 'sensor_data/audio_intensity_data.csv',
            'goals': 'earnings/driver_goals.csv',
            'earnings_log': 'earnings/earnings_velocity_log.csv'
        }
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all required data files and return as dictionary."""
        data = {}
        
        for key, relative_path in self.required_files.items():
            full_path = os.path.join(self.data_dir, relative_path)
            
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Required data file not found: {full_path}")
            
            try:
                df = pd.read_csv(full_path)
                data[key] = df
                print(f"✓ Loaded {key}: {len(df)} rows from {full_path}")
            except Exception as e:
                raise ValueError(f"Error loading {key} from {full_path}: {str(e)}")
        
        return data
    
    def validate_data_structure(self, data: Dict[str, pd.DataFrame]) -> bool:
        """Validate that all dataframes have required columns."""
        required_columns = {
            'trips': ['trip_id', 'driver_id', 'start_time', 'end_time', 'fare'],
            'drivers': ['driver_id', 'rating', 'city'],
            'accelerometer': ['timestamp', 'ax', 'ay', 'az'],
            'audio': ['timestamp', 'decibel_level'],
            'goals': ['driver_id', 'daily_goal'],
            'earnings_log': ['timestamp', 'driver_id', 'earnings']
        }
        
        for key, df in data.items():
            if key in required_columns:
                missing_cols = set(required_columns[key]) - set(df.columns)
                if missing_cols:
                    raise ValueError(f"Missing required columns in {key}: {missing_cols}")
        
        return True
    
    def get_data_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Generate summary statistics for all loaded data."""
        summary = {}
        
        for key, df in data.items():
            summary[key] = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
                'null_counts': df.isnull().sum().to_dict(),
                'dtypes': df.dtypes.to_dict()
            }
        
        return summary
