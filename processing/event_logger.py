"""
Event Logger Module
Generates structured output logs for all detected events.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import os


class EventLogger:
    """Handles logging and formatting of detected events."""
    
    def __init__(self, output_dir: str = "./outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Event log format
        self.log_columns = [
            'timestamp',
            'end_timestamp', 
            'signal_type',
            'raw_value',
            'threshold',
            'event_label',
            'severity',
            'confidence',
            'duration_seconds',
            'additional_data'
        ]
    
    def _serialize_event(self, event: Dict) -> Dict:
        """Convert event with timestamps to JSON-serializable format."""
        if event is None:
            return None
        
        serialized = {}
        for key, value in event.items():
            if hasattr(value, 'isoformat'):  # Timestamp/datetime objects
                serialized[key] = str(value)
            elif hasattr(value, 'item'):  # numpy types (int64, float64, etc.)
                serialized[key] = value.item()
            elif isinstance(value, dict):
                serialized[key] = self._serialize_event(value)
            elif isinstance(value, list):
                serialized[key] = [self._serialize_event(item) if isinstance(item, dict) else item for item in value]
            else:
                serialized[key] = value
        return serialized
    
    def ensure_output_directory(self):
        """Ensure output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def log_accelerometer_events(self, accel_events: List[Dict], 
                                 accel_df: pd.DataFrame) -> pd.DataFrame:
        """Log accelerometer events to structured format."""
        event_logs = []
        
        for event in accel_events:
            # Find the raw data point that triggered this event
            raw_data = self._find_raw_data_point(
                accel_df, event['timestamp'], 'accelerometer'
            )
            
            log_entry = {
                'timestamp': str(event['timestamp']),
                'end_timestamp': str(event['end_timestamp']),
                'signal_type': 'ACCELEROMETER',
                'raw_value': event.get('peak_magnitude', 0),
                'threshold': self._get_accelerometer_threshold(event['event_type']),
                'event_label': event['event_type'].upper(),
                'severity': event['severity'],
                'confidence': event['confidence'],
                'duration_seconds': event['duration_seconds'],
                'additional_data': json.dumps({
                    'peak_magnitude': event.get('peak_magnitude'),
                    'event_type': event['event_type'],
                    'detection_method': 'accelerometer_analysis'
                })
            }
            
            event_logs.append(log_entry)
        
        return pd.DataFrame(event_logs)
    
    def log_audio_events(self, audio_events: List[Dict], 
                         audio_df: pd.DataFrame) -> pd.DataFrame:
        """Log audio events to structured format."""
        event_logs = []
        
        for event in audio_events:
            # Find the raw data point that triggered this event
            raw_data = self._find_raw_data_point(
                audio_df, event['timestamp'], 'audio'
            )
            
            log_entry = {
                'timestamp': str(event['timestamp']),
                'end_timestamp': str(event['end_timestamp']),
                'signal_type': 'AUDIO',
                'raw_value': event.get('peak_decibel', 0),
                'threshold': self._get_audio_threshold(event['event_type']),
                'event_label': event['event_type'].upper(),
                'severity': event['severity'],
                'confidence': event['confidence'],
                'duration_seconds': event['duration_seconds'],
                'additional_data': json.dumps({
                    'peak_decibel': event.get('peak_decibel'),
                    'avg_decibel': event.get('avg_decibel'),
                    'event_type': event['event_type'],
                    'detection_method': 'audio_analysis'
                })
            }
            
            event_logs.append(log_entry)
        
        return pd.DataFrame(event_logs)
    
    def log_fused_events(self, fused_events: List[Dict]) -> pd.DataFrame:
        """Log fused stress events to structured format."""
        event_logs = []
        
        for event in fused_events:
            # Determine primary signal and value
            if event.get('accelerometer_event') and event.get('audio_event'):
                signal_type = 'FUSED_ACCEL_AUDIO'
                raw_value = max(
                    event['accelerometer_event'].get('peak_magnitude', 0),
                    event['audio_event'].get('peak_decibel', 0)
                )
                threshold = 'COMBINED_THRESHOLD'
            elif event.get('accelerometer_event'):
                signal_type = 'SINGLE_ACCELEROMETER'
                raw_value = event['accelerometer_event'].get('peak_magnitude', 0)
                threshold = self._get_accelerometer_threshold(
                    event['accelerometer_event']['event_type']
                )
            elif event.get('audio_event'):
                signal_type = 'SINGLE_AUDIO'
                raw_value = event['audio_event'].get('peak_decibel', 0)
                threshold = self._get_audio_threshold(
                    event['audio_event']['event_type']
                )
            else:
                continue
            
            log_entry = {
                'timestamp': str(event['timestamp']),
                'end_timestamp': str(event['end_timestamp']),
                'signal_type': signal_type,
                'raw_value': raw_value,
                'threshold': threshold,
                'event_label': event['event_type'].upper(),
                'severity': event['severity'],
                'confidence': event['combined_confidence'],
                'duration_seconds': event['duration_seconds'],
                'additional_data': json.dumps({
                    'stress_level': event.get('stress_level'),
                    'signal_combination': event.get('signal_combination'),
                    'accelerometer_event': self._serialize_event(event.get('accelerometer_event')),
                    'audio_event': self._serialize_event(event.get('audio_event')),
                    'detection_method': 'multi_signal_fusion'
                })
            }
            
            event_logs.append(log_entry)
        
        return pd.DataFrame(event_logs)
    
    def _find_raw_data_point(self, df: pd.DataFrame, timestamp: datetime, 
                           signal_type: str) -> Dict:
        """Find the raw data point closest to the event timestamp."""
        if df.empty:
            return {}
        
        # Find the closest data point to the event timestamp
        time_diffs = abs(df['timestamp'] - timestamp)
        closest_idx = time_diffs.idxmin()
        
        raw_point = df.loc[closest_idx].to_dict()
        
        # Add signal type specific information
        if signal_type == 'accelerometer':
            raw_point['horizontal_magnitude'] = np.sqrt(
                raw_point.get('ax', 0)**2 + raw_point.get('ay', 0)**2
            )
        elif signal_type == 'audio':
            raw_point['decibel_level'] = raw_point.get('decibel_level', 0)
        
        return raw_point
    
    def _get_accelerometer_threshold(self, event_type: str) -> float:
        """Get the threshold for accelerometer event types."""
        thresholds = {
            'harsh_braking': -2.0,
            'harsh_acceleration': 2.0,
            'moderate_braking': -1.5,
            'moderate_acceleration': 1.5
        }
        return thresholds.get(event_type, 0.0)
    
    def _get_audio_threshold(self, event_type: str) -> float:
        """Get the threshold for audio event types."""
        thresholds = {
            'noise_spike': 80,
            'sustained_high_noise': 70,
            'extreme_noise': 90
        }
        return thresholds.get(event_type, 0.0)
    
    def create_flagged_moments_log(self, accel_events: List[Dict], 
                                  audio_events: List[Dict],
                                  fused_events: List[Dict],
                                  accel_df: pd.DataFrame,
                                  audio_df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive flagged moments log."""
        all_logs = []
        
        # Log accelerometer events
        accel_logs = self.log_accelerometer_events(accel_events, accel_df)
        if not accel_logs.empty:
            all_logs.append(accel_logs)
        
        # Log audio events  
        audio_logs = self.log_audio_events(audio_events, audio_df)
        if not audio_logs.empty:
            all_logs.append(audio_logs)
        
        # Log fused events
        fused_logs = self.log_fused_events(fused_events)
        if not fused_logs.empty:
            all_logs.append(fused_logs)
        
        # Combine all logs
        if all_logs:
            combined_logs = pd.concat(all_logs, ignore_index=True)
            combined_logs = combined_logs.sort_values('timestamp').reset_index(drop=True)
        else:
            combined_logs = pd.DataFrame(columns=self.log_columns)
        
        # Save to file
        output_path = os.path.join(self.output_dir, 'flagged_moments.csv')
        combined_logs.to_csv(output_path, index=False)
        
        print(f"✓ Saved {len(combined_logs)} flagged events to {output_path}")
        
        return combined_logs
    
    def create_event_summary(self, flagged_logs: pd.DataFrame) -> Dict:
        """Create summary statistics for all events."""
        if flagged_logs.empty:
            return {}
        
        summary = {
            'total_events': len(flagged_logs),
            'events_by_type': flagged_logs['event_label'].value_counts().to_dict(),
            'events_by_severity': flagged_logs['severity'].value_counts().to_dict(),
            'events_by_signal_type': flagged_logs['signal_type'].value_counts().to_dict(),
            'avg_confidence': flagged_logs['confidence'].mean(),
            'avg_duration_seconds': flagged_logs['duration_seconds'].mean(),
            'total_event_duration_hours': flagged_logs['duration_seconds'].sum() / 3600,
            'events_per_hour': len(flagged_logs) / max(1, flagged_logs['duration_seconds'].sum() / 3600)
        }
        
        # Time-based analysis
        flagged_logs['hour'] = pd.to_datetime(flagged_logs['timestamp']).dt.hour
        summary['events_by_hour'] = flagged_logs['hour'].value_counts().to_dict()
        
        return summary
    
    def export_event_logs(self, flagged_logs: pd.DataFrame, 
                         format_type: str = 'csv') -> str:
        """Export event logs in specified format."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format_type.lower() == 'csv':
            filename = f'flagged_moments_{timestamp}.csv'
            output_path = os.path.join(self.output_dir, filename)
            flagged_logs.to_csv(output_path, index=False)
        
        elif format_type.lower() == 'json':
            filename = f'flagged_moments_{timestamp}.json'
            output_path = os.path.join(self.output_dir, filename)
            flagged_logs.to_json(output_path, orient='records', date_format='iso')
        
        elif format_type.lower() == 'parquet':
            filename = f'flagged_moments_{timestamp}.parquet'
            output_path = os.path.join(self.output_dir, filename)
            flagged_logs.to_parquet(output_path, index=False)
        
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        print(f"✓ Exported event logs to {output_path}")
        return output_path
