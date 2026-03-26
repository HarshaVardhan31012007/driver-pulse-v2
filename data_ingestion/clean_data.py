"""
Data Cleaning Module for Driver Pulse
Handles data cleaning, timestamp normalization, and missing data handling.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Tuple, Optional
import warnings


class DataCleaner:
    """Handles cleaning and preprocessing of all driver pulse data."""
    
    def __init__(self):
        self.timestamp_formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f'
        ]
    
    def clean_all_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Clean all dataframes and return cleaned versions."""
        cleaned_data = {}
        
        # Clean each dataset with specific logic
        cleaned_data['trips'] = self._clean_trips_data(data['trips'])
        cleaned_data['drivers'] = self._clean_drivers_data(data['drivers'])
        cleaned_data['accelerometer'] = self._clean_accelerometer_data(data['accelerometer'])
        cleaned_data['audio'] = self._clean_audio_data(data['audio'])
        cleaned_data['goals'] = self._clean_goals_data(data['goals'])
        cleaned_data['earnings_log'] = self._clean_earnings_log_data(data['earnings_log'])
        
        return cleaned_data
    
    def _normalize_timestamps(self, df: pd.DataFrame, timestamp_col: str) -> pd.DataFrame:
        """Normalize timestamp columns to datetime format."""
        df = df.copy()
        
        # Try different timestamp formats
        for fmt in self.timestamp_formats:
            try:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col], format=fmt)
                break
            except (ValueError, TypeError):
                continue
        else:
            # If none of the formats work, try pandas auto-detection
            try:
                df[timestamp_col] = pd.to_datetime(df[timestamp_col])
            except Exception as e:
                warnings.warn(f"Could not parse timestamps in {timestamp_col}: {str(e)}")
        
        # Remove rows with invalid timestamps
        df = df.dropna(subset=[timestamp_col])
        
        return df
    
    def _clean_trips_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean trips data."""
        df = df.copy()
        
        # Normalize timestamps
        df = self._normalize_timestamps(df, 'start_time')
        df = self._normalize_timestamps(df, 'end_time')
        
        # Remove invalid trips
        df = df.dropna(subset=['trip_id', 'driver_id', 'fare'])
        df = df[df['fare'] >= 0]  # Remove negative fares
        
        # Calculate trip duration
        df['duration_minutes'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 60
        df = df[df['duration_minutes'] > 0]  # Remove trips with negative duration
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['trip_id'])
        
        print(f"✓ Cleaned trips: {len(df)} valid trips remaining")
        return df
    
    def _clean_drivers_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean drivers data."""
        df = df.copy()
        
        # Remove invalid entries
        df = df.dropna(subset=['driver_id'])
        
        # Clean rating column
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
            df = df[(df['rating'] >= 1) & (df['rating'] <= 5)]  # Valid rating range
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['driver_id'])
        
        print(f"✓ Cleaned drivers: {len(df)} valid drivers remaining")
        return df
    
    def _clean_accelerometer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean accelerometer data."""
        df = df.copy()
        
        # Normalize timestamps
        df = self._normalize_timestamps(df, 'timestamp')
        
        # Clean acceleration values
        accel_cols = ['ax', 'ay', 'az']
        for col in accel_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing acceleration data
        df = df.dropna(subset=accel_cols)
        
        # Remove extreme outliers (beyond realistic vehicle acceleration)
        accel_magnitude = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
        df = df[accel_magnitude <= 50]  # Remove readings > 50 m/s²
        
        print(f"✓ Cleaned accelerometer: {len(df)} valid readings remaining")
        return df
    
    def _clean_audio_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean audio intensity data."""
        df = df.copy()
        
        # Normalize timestamps
        df = self._normalize_timestamps(df, 'timestamp')
        
        # Clean decibel levels
        if 'decibel_level' in df.columns:
            df['decibel_level'] = pd.to_numeric(df['decibel_level'], errors='coerce')
            
            # Remove invalid decibel levels
            df = df.dropna(subset=['decibel_level'])
            df = df[(df['decibel_level'] >= 0) & (df['decibel_level'] <= 140)]  # Realistic dB range
        
        print(f"✓ Cleaned audio: {len(df)} valid readings remaining")
        return df
    
    def _clean_goals_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean driver goals data."""
        df = df.copy()
        
        # Remove invalid entries
        df = df.dropna(subset=['driver_id', 'daily_goal'])
        
        # Clean goal values
        df['daily_goal'] = pd.to_numeric(df['daily_goal'], errors='coerce')
        df = df[df['daily_goal'] > 0]  # Remove negative or zero goals
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['driver_id'])
        
        print(f"✓ Cleaned goals: {len(df)} valid goals remaining")
        return df
    
    def _clean_earnings_log_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean earnings velocity log data."""
        df = df.copy()
        
        # Normalize timestamps
        df = self._normalize_timestamps(df, 'timestamp')
        
        # Clean earnings data
        df = df.dropna(subset=['driver_id', 'earnings'])
        df['earnings'] = pd.to_numeric(df['earnings'], errors='coerce')
        df = df[df['earnings'] >= 0]  # Remove negative earnings
        
        print(f"✓ Cleaned earnings log: {len(df)} valid entries remaining")
        return df
    
    def normalize_signals(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Normalize sensor signals for consistent processing."""
        normalized_data = data.copy()
        
        # Normalize accelerometer values to g-force (assuming input is in m/s²)
        if 'accelerometer' in normalized_data:
            accel_cols = ['ax', 'ay', 'az']
            for col in accel_cols:
                if col in normalized_data['accelerometer'].columns:
                    normalized_data['accelerometer'][col] = normalized_data['accelerometer'][col] / 9.81
        
        # Normalize audio levels if needed
        if 'audio' in normalized_data and 'decibel_level' in normalized_data['audio'].columns:
            # Audio is already in dB, no normalization needed
            pass
        
        return normalized_data
