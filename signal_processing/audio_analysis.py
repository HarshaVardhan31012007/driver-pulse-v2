"""
Audio Signal Analysis Module
Detects noise spikes and sustained high-intensity audio events.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy import signal
import warnings


class AudioAnalyzer:
    """Analyzes audio intensity data to detect noise events."""
    
    def __init__(self):
        # Audio thresholds (in dB)
        self.NOISE_SPIKE_THRESHOLD = 80      # dB for sudden spikes
        self.SUSTAINED_HIGH_THRESHOLD = 70    # dB for sustained high noise
        self.EXTREME_NOISE_THRESHOLD = 90     # dB for extreme noise
        
        # Time-based parameters
        self.SUSTAINED_DURATION_MIN = 3.0     # seconds for sustained high noise
        self.SPIKE_WINDOW_SIZE = 1.0          # seconds for spike detection
        
        # Signal processing parameters
        self.SAMPLING_RATE = 2                # Hz (assuming 2Hz sampling)
        self.ROLLING_WINDOW_SIZE = 5          # samples for smoothing
        
    def smooth_signal(self, df: pd.DataFrame, column: str = 'decibel_level') -> pd.DataFrame:
        """Apply smoothing filter to reduce noise."""
        df = df.copy()
        
        # Rolling mean for basic smoothing
        df[f'{column}_smooth'] = df[column].rolling(
            window=self.ROLLING_WINDOW_SIZE,
            center=True,
            min_periods=1
        ).mean()
        
        # Additional exponential moving average for better noise reduction
        df[f'{column}_smooth'] = df[f'{column}_smooth'].ewm(
            alpha=0.3,
            adjust=False
        ).mean()
        
        return df
    
    def detect_noise_spikes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect sudden noise spikes."""
        df = df.copy()
        
        if 'decibel_level_smooth' not in df.columns:
            df = self.smooth_signal(df)
        
        # Calculate rate of change (derivative) to detect spikes
        df['db_rate_of_change'] = df['decibel_level_smooth'].diff()
        
        # Detect sudden increases
        spike_threshold = 10  # dB increase in one sample
        spike_mask = (
            (df['decibel_level_smooth'] > self.NOISE_SPIKE_THRESHOLD) &
            (df['db_rate_of_change'] > spike_threshold)
        )
        
        # Mark spike events
        df['noise_spike'] = False
        df.loc[spike_mask, 'noise_spike'] = True
        
        return df
    
    def detect_sustained_high_noise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect sustained periods of high noise."""
        df = df.copy()
        
        if 'decibel_level_smooth' not in df.columns:
            df = self.smooth_signal(df)
        
        # Identify periods above threshold
        high_noise_mask = df['decibel_level_smooth'] > self.SUSTAINED_HIGH_THRESHOLD
        
        # Find continuous segments
        df['high_noise_segment'] = (
            high_noise_mask != high_noise_mask.shift()
        ).cumsum()
        
        # Calculate duration of each segment
        segment_stats = df.groupby('high_noise_segment').agg({
            'timestamp': ['min', 'max', 'count'],
            'decibel_level_smooth': 'mean'
        }).reset_index()
        
        # Identify segments that meet duration criteria
        segment_stats.columns = ['segment_id', 'start_time', 'end_time', 'sample_count', 'avg_db']
        segment_stats['duration_seconds'] = (
            segment_stats['end_time'] - segment_stats['start_time']
        ).dt.total_seconds()
        
        valid_segments = segment_stats[
            segment_stats['duration_seconds'] >= self.SUSTAINED_DURATION_MIN
        ]
        
        # Mark sustained high noise periods
        df['sustained_high_noise'] = False
        for _, segment in valid_segments.iterrows():
            if segment['segment_id'] != 0:  # segment_id 0 is below threshold
                mask = df['high_noise_segment'] == segment['segment_id']
                df.loc[mask, 'sustained_high_noise'] = True
        
        return df
    
    def detect_extreme_noise(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detect extreme noise events."""
        df = df.copy()
        
        if 'decibel_level_smooth' not in df.columns:
            df = self.smooth_signal(df)
        
        # Mark extreme noise events
        df['extreme_noise'] = df['decibel_level_smooth'] > self.EXTREME_NOISE_THRESHOLD
        
        return df
    
    def classify_audio_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Classify different types of audio events."""
        df = df.copy()
        
        # Run all detection methods
        df = self.detect_noise_spikes(df)
        df = self.detect_sustained_high_noise(df)
        df = self.detect_extreme_noise(df)
        
        # Classify events
        df['audio_event_type'] = 'normal'
        df['audio_severity'] = 'none'
        df['audio_confidence'] = 0.0
        
        # Extreme noise has highest priority
        extreme_mask = df['extreme_noise']
        df.loc[extreme_mask, 'audio_event_type'] = 'extreme_noise'
        df.loc[extreme_mask, 'audio_severity'] = 'high'
        df.loc[extreme_mask, 'audio_confidence'] = np.minimum(
            (df.loc[extreme_mask, 'decibel_level_smooth'] - self.EXTREME_NOISE_THRESHOLD) / 10.0,
            1.0
        )
        
        # Noise spikes
        spike_mask = df['noise_spike'] & ~extreme_mask
        df.loc[spike_mask, 'audio_event_type'] = 'noise_spike'
        df.loc[spike_mask, 'audio_severity'] = 'medium'
        df.loc[spike_mask, 'audio_confidence'] = np.minimum(
            (df.loc[spike_mask, 'db_rate_of_change'] - 10) / 20.0,
            1.0
        )
        
        # Sustained high noise
        sustained_mask = df['sustained_high_noise'] & ~extreme_mask & ~spike_mask
        df.loc[sustained_mask, 'audio_event_type'] = 'sustained_high_noise'
        df.loc[sustained_mask, 'audio_severity'] = 'medium'
        df.loc[sustained_mask, 'audio_confidence'] = np.minimum(
            (df.loc[sustained_mask, 'decibel_level_smooth'] - self.SUSTAINED_HIGH_THRESHOLD) / 20.0,
            1.0
        )
        
        return df
    
    def extract_audio_events(self, df: pd.DataFrame) -> List[Dict]:
        """Extract discrete audio events from continuous detection."""
        events = []
        
        # Find continuous segments of the same event type
        df_sorted = df.sort_values('timestamp').reset_index(drop=True)
        
        # Group consecutive events
        event_groups = df_sorted.groupby(
            (df_sorted['audio_event_type'] != df_sorted['audio_event_type'].shift()).cumsum()
        )
        
        for _, group in event_groups:
            if group['audio_event_type'].iloc[0] != 'normal':
                event = {
                    'timestamp': group['timestamp'].iloc[0],
                    'end_timestamp': group['timestamp'].iloc[-1],
                    'event_type': group['audio_event_type'].iloc[0],
                    'severity': group['audio_severity'].iloc[0],
                    'confidence': group['audio_confidence'].max(),
                    'peak_decibel': group['decibel_level_smooth'].max(),
                    'avg_decibel': group['decibel_level_smooth'].mean(),
                    'duration_seconds': (group['timestamp'].iloc[-1] - group['timestamp'].iloc[0]).total_seconds(),
                    'signal_type': 'audio'
                }
                
                # Filter very short events (less than 0.5 seconds)
                if event['duration_seconds'] >= 0.5:
                    events.append(event)
        
        return events
    
    def analyze_audio_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """Complete analysis pipeline for audio data."""
        # Smooth signal
        df_processed = self.smooth_signal(df)
        
        # Classify events
        df_processed = self.classify_audio_events(df_processed)
        
        # Extract discrete events
        events = self.extract_audio_events(df_processed)
        
        print(f"✓ Detected {len(events)} audio events")
        
        return df_processed, events
