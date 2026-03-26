"""
Multi-Signal Event Fusion Module
Combines accelerometer and audio events to detect driver stress events.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta


class EventFusion:
    """Fuses multiple signal events to detect comprehensive driver stress events."""
    
    def __init__(self):
        # Fusion parameters
        self.COINCIDENCE_WINDOW_SECONDS = 5.0    # Time window for event coincidence
        self.STRESS_COMBINATION_RULES = {
            'harsh_braking + noise_spike': 'high_stress',
            'harsh_acceleration + noise_spike': 'high_stress', 
            'harsh_braking + sustained_high_noise': 'high_stress',
            'harsh_acceleration + sustained_high_noise': 'medium_stress',
            'moderate_braking + noise_spike': 'medium_stress',
            'moderate_acceleration + noise_spike': 'medium_stress',
            'extreme_noise + harsh_braking': 'critical_stress',
            'extreme_noise + harsh_acceleration': 'critical_stress'
        }
        
        # Severity weights
        self.SIGNAL_WEIGHTS = {
            'accelerometer': 0.6,
            'audio': 0.4
        }
        
        # Confidence thresholds
        self.MIN_FUSION_CONFIDENCE = 0.5
        self.HIGH_STRESS_THRESHOLD = 0.8
        self.MEDIUM_STRESS_THRESHOLD = 0.6
    
    def find_coincident_events(self, accel_events: List[Dict], audio_events: List[Dict]) -> List[Dict]:
        """Find events that occur within the coincidence window."""
        coincident_events = []
        
        for accel_event in accel_events:
            coincident_audio = []
            
            for audio_event in audio_events:
                # Check if events are within coincidence window
                time_diff = abs((accel_event['timestamp'] - audio_event['timestamp']).total_seconds())
                
                if time_diff <= self.COINCIDENCE_WINDOW_SECONDS:
                    coincident_audio.append(audio_event)
            
            if coincident_audio:
                # Create fused event
                fused_event = self._create_fused_event(accel_event, coincident_audio)
                coincident_events.append(fused_event)
        
        return coincident_events
    
    def _create_fused_event(self, accel_event: Dict, coincident_audio: List[Dict]) -> Dict:
        """Create a fused event from accelerometer and audio events."""
        # Find the most significant audio event
        primary_audio = max(coincident_audio, key=lambda x: x['confidence'])
        
        # Determine stress level based on combination
        accel_type = accel_event['event_type']
        audio_type = primary_audio['event_type']
        
        combination_key = f"{accel_type} + {audio_type}"
        stress_level = self.STRESS_COMBINATION_RULES.get(combination_key, 'low_stress')
        
        # Calculate combined confidence
        accel_confidence = accel_event['confidence'] * self.SIGNAL_WEIGHTS['accelerometer']
        audio_confidence = primary_audio['confidence'] * self.SIGNAL_WEIGHTS['audio']
        combined_confidence = accel_confidence + audio_confidence
        
        # Determine event time window
        start_time = min(accel_event['timestamp'], primary_audio['timestamp'])
        end_time = max(accel_event['end_timestamp'], primary_audio['end_timestamp'])
        
        fused_event = {
            'timestamp': start_time,
            'end_timestamp': end_time,
            'event_type': 'driver_stress_event',
            'stress_level': stress_level,
            'combined_confidence': combined_confidence,
            'accelerometer_event': accel_event,
            'audio_event': primary_audio,
            'duration_seconds': (end_time - start_time).total_seconds(),
            'signal_combination': combination_key,
            'severity': self._map_stress_to_severity(stress_level, combined_confidence)
        }
        
        return fused_event
    
    def _map_stress_to_severity(self, stress_level: str, confidence: float) -> str:
        """Map stress level and confidence to severity."""
        if stress_level == 'critical_stress' and confidence > self.HIGH_STRESS_THRESHOLD:
            return 'critical'
        elif stress_level == 'high_stress' and confidence > self.MEDIUM_STRESS_THRESHOLD:
            return 'high'
        elif stress_level == 'medium_stress' and confidence > self.MIN_FUSION_CONFIDENCE:
            return 'medium'
        else:
            return 'low'
    
    def add_single_signal_events(self, accel_events: List[Dict], audio_events: List[Dict]) -> List[Dict]:
        """Add significant single-signal events that don't have coincident partners."""
        single_events = []
        
        # Add high-confidence accelerometer events
        for accel_event in accel_events:
            if accel_event['confidence'] > 0.8 and accel_event['severity'] in ['high', 'medium']:
                single_event = {
                    'timestamp': accel_event['timestamp'],
                    'end_timestamp': accel_event['end_timestamp'],
                    'event_type': 'single_signal_event',
                    'stress_level': 'low_stress',
                    'combined_confidence': accel_event['confidence'] * 0.7,  # Reduce confidence for single signal
                    'accelerometer_event': accel_event,
                    'audio_event': None,
                    'duration_seconds': accel_event['duration_seconds'],
                    'signal_combination': f"single_{accel_event['event_type']}",
                    'severity': accel_event['severity']
                }
                single_events.append(single_event)
        
        # Add extreme audio events
        for audio_event in audio_events:
            if audio_event['event_type'] == 'extreme_noise' and audio_event['confidence'] > 0.7:
                single_event = {
                    'timestamp': audio_event['timestamp'],
                    'end_timestamp': audio_event['end_timestamp'],
                    'event_type': 'single_signal_event',
                    'stress_level': 'medium_stress',
                    'combined_confidence': audio_event['confidence'] * 0.7,
                    'accelerometer_event': None,
                    'audio_event': audio_event,
                    'duration_seconds': audio_event['duration_seconds'],
                    'signal_combination': f"single_{audio_event['event_type']}",
                    'severity': audio_event['severity']
                }
                single_events.append(single_event)
        
        return single_events
    
    def merge_overlapping_events(self, events: List[Dict]) -> List[Dict]:
        """Merge overlapping events to avoid double-counting."""
        if not events:
            return []
        
        # Sort events by timestamp
        events_sorted = sorted(events, key=lambda x: x['timestamp'])
        merged_events = []
        
        current_event = events_sorted[0].copy()
        
        for next_event in events_sorted[1:]:
            # Check if events overlap
            if next_event['timestamp'] <= current_event['end_timestamp']:
                # Merge events
                current_event['end_timestamp'] = max(
                    current_event['end_timestamp'], 
                    next_event['end_timestamp']
                )
                current_event['duration_seconds'] = (
                    current_event['end_timestamp'] - current_event['timestamp']
                ).total_seconds()
                
                # Keep the higher confidence and severity
                if next_event['combined_confidence'] > current_event['combined_confidence']:
                    current_event['combined_confidence'] = next_event['combined_confidence']
                    current_event['stress_level'] = next_event['stress_level']
                    current_event['severity'] = next_event['severity']
            else:
                # No overlap, add current event and start new one
                merged_events.append(current_event)
                current_event = next_event.copy()
        
        # Add the last event
        merged_events.append(current_event)
        
        return merged_events
    
    def fuse_signals(self, accel_events: List[Dict], audio_events: List[Dict]) -> List[Dict]:
        """Main fusion method to combine accelerometer and audio events."""
        # Find coincident events
        coincident_events = self.find_coincident_events(accel_events, audio_events)
        
        # Add significant single-signal events
        single_events = self.add_single_signal_events(accel_events, audio_events)
        
        # Combine all events
        all_events = coincident_events + single_events
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        # Merge overlapping events
        fused_events = self.merge_overlapping_events(all_events)
        
        # Filter by minimum confidence
        filtered_events = [
            event for event in fused_events 
            if event['combined_confidence'] >= self.MIN_FUSION_CONFIDENCE
        ]
        
        print(f"✓ Fused {len(filtered_events)} stress events from {len(accel_events)} accel and {len(audio_events)} audio events")
        
        return filtered_events
    
    def create_event_dataframe(self, events: List[Dict]) -> pd.DataFrame:
        """Convert fused events to a structured DataFrame."""
        if not events:
            return pd.DataFrame()
        
        # Flatten events for DataFrame
        flattened_events = []
        for event in events:
            flat_event = {
                'timestamp': event['timestamp'],
                'end_timestamp': event['end_timestamp'],
                'event_type': event['event_type'],
                'stress_level': event['stress_level'],
                'combined_confidence': event['combined_confidence'],
                'duration_seconds': event['duration_seconds'],
                'signal_combination': event['signal_combination'],
                'severity': event['severity']
            }
            
            # Add accelerometer details if available
            if event.get('accelerometer_event'):
                flat_event.update({
                    'accel_event_type': event['accelerometer_event']['event_type'],
                    'accel_peak_magnitude': event['accelerometer_event'].get('peak_magnitude'),
                    'accel_confidence': event['accelerometer_event']['confidence']
                })
            
            # Add audio details if available
            if event.get('audio_event'):
                flat_event.update({
                    'audio_event_type': event['audio_event']['event_type'],
                    'audio_peak_decibel': event['audio_event'].get('peak_decibel'),
                    'audio_avg_decibel': event['audio_event'].get('avg_decibel'),
                    'audio_confidence': event['audio_event']['confidence']
                })
            
            flattened_events.append(flat_event)
        
        return pd.DataFrame(flattened_events)
