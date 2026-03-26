"""
Advanced Accelerometer Signal Analysis Module
Enhanced event detection with ML-inspired features for hackathon excellence.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from scipy import signal, stats
from sklearn.preprocessing import StandardScaler
import warnings


class AccelerometerAnalyzer:
    """Advanced accelerometer analysis with enhanced event detection."""
    
    def __init__(self):
        # Enhanced detection thresholds (adaptive based on driving patterns)
        self.HARSH_BRAKE_THRESHOLD = -2.0  # g
        self.HARSH_ACCEL_THRESHOLD = 2.0   # g
        self.MODERATE_BRAKE_THRESHOLD = -1.5  # g
        self.MODERATE_ACCEL_THRESHOLD = 1.5   # g
        
        # Advanced signal processing parameters
        self.SAMPLING_RATE = 10  # Hz
        self.ROLLING_WINDOW_SIZE = 5
        self.MIN_EVENT_DURATION = 0.5  # seconds
        self.PEAK_DETECTION_HEIGHT = 0.5  # Minimum peak height
        self.PEAK_DETECTION_DISTANCE = 3  # Minimum samples between peaks
        
        # ML-inspired features
        self.scaler = StandardScaler()
        self.event_patterns = {
            'harsh_braking': {'duration': (0.3, 2.0), 'intensity': (2.0, 5.0)},
            'harsh_acceleration': {'duration': (0.2, 1.5), 'intensity': (2.0, 4.0)},
            'cornering': {'lateral_g': (0.8, 2.5), 'duration': (1.0, 3.0)},
            'bump_detection': {'vertical_g': (1.5, 4.0), 'frequency': (5, 15)}
        }
        
    def compute_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute advanced features for better event detection."""
        df = df.copy()
        
        # Basic magnitude calculations
        df['magnitude'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
        df['horizontal_magnitude'] = np.sqrt(df['ax']**2 + df['ay']**2)
        df['lateral_g'] = np.abs(df['ay'])  # Side-to-side acceleration
        df['vertical_g'] = np.abs(df['az'] - 9.8)  # Vertical bumps (remove gravity)
        
        # Rate of change (jerk) - important for harsh events
        df['jerk_x'] = np.gradient(df['ax'])
        df['jerk_y'] = np.gradient(df['ay'])
        df['jerk_z'] = np.gradient(df['az'])
        df['jerk_magnitude'] = np.sqrt(df['jerk_x']**2 + df['jerk_y']**2 + df['jerk_z']**2)
        
        # Statistical features in rolling windows
        for window in [3, 5, 10]:
            df[f'magnitude_std_{window}'] = df['magnitude'].rolling(window, min_periods=1).std()
            df[f'magnitude_var_{window}'] = df['magnitude'].rolling(window, min_periods=1).var()
            df[f'jerk_max_{window}'] = df['jerk_magnitude'].rolling(window, min_periods=1).max()
        
        # Frequency domain features
        if len(df) > 20:
            # FFT for vibration analysis
            fft_vals = np.fft.fft(df['magnitude'].values)
            fft_freq = np.fft.fftfreq(len(df), 1/self.SAMPLING_RATE)
            
            # Dominant frequency and power
            dominant_freq_idx = np.argmax(np.abs(fft_vals[1:len(fft_vals)//2])) + 1
            df['dominant_frequency'] = fft_freq[dominant_freq_idx]
            df['frequency_power'] = np.abs(fft_vals[dominant_freq_idx])
        
        return df
    
    def advanced_smoothing(self, df: pd.DataFrame, column: str = 'horizontal_magnitude') -> pd.DataFrame:
        """Apply advanced multi-stage smoothing."""
        df = df.copy()
        
        # Stage 1: Median filter for spike removal
        df[f'{column}_median'] = df[column].rolling(window=3, center=True, min_periods=1).median()
        
        # Stage 2: Savitzky-Golay for preserving peaks
        if len(df) > 7:
            window_length = min(11, len(df) if len(df) % 2 == 1 else len(df) - 1)
            df[f'{column}_smooth'] = signal.savgol_filter(
                df[f'{column}_median'], 
                window_length=window_length,
                polyorder=3
            )
        else:
            df[f'{column}_smooth'] = df[f'{column}_median']
        
        # Stage 3: Exponential weighted moving average for final smoothing
        df[f'{column}_final'] = df[f'{column}_smooth'].ewm(alpha=0.3, adjust=False).mean()
        
        return df
    
    def detect_peaks_advanced(self, df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """Advanced peak detection for different event types."""
        peaks = {}
        
        # Braking peaks (negative peaks in horizontal magnitude)
        if len(df) > 10:
            brake_peaks, _ = signal.find_peaks(
                -df['horizontal_magnitude_final'], 
                height=self.PEAK_DETECTION_HEIGHT,
                distance=self.PEAK_DETECTION_DISTANCE
            )
            peaks['braking'] = brake_peaks
            
            # Acceleration peaks (positive peaks)
            accel_peaks, _ = signal.find_peaks(
                df['horizontal_magnitude_final'], 
                height=self.PEAK_DETECTION_HEIGHT,
                distance=self.PEAK_DETECTION_DISTANCE
            )
            peaks['acceleration'] = accel_peaks
            
            # Lateral peaks (cornering)
            lateral_peaks, _ = signal.find_peaks(
                df['lateral_g'], 
                height=0.8,
                distance=self.PEAK_DETECTION_DISTANCE
            )
            peaks['cornering'] = lateral_peaks
            
            # Vertical peaks (bumps)
            vertical_peaks, _ = signal.find_peaks(
                df['vertical_g'], 
                height=1.5,
                distance=self.PEAK_DETECTION_DISTANCE
            )
            peaks['bumps'] = vertical_peaks
        
        return peaks
    
    def classify_events_ml_inspired(self, df: pd.DataFrame, peaks: Dict[str, np.ndarray]) -> List[Dict]:
        """ML-inspired event classification with confidence scoring."""
        events = []
        
        for event_type, peak_indices in peaks.items():
            for peak_idx in peak_indices:
                if peak_idx >= len(df):
                    continue
                    
                event_start = max(0, peak_idx - 2)
                event_end = min(len(df), peak_idx + 3)
                event_segment = df.iloc[event_start:event_end]
                
                # Extract features for classification
                features = self._extract_event_features(event_segment, event_type)
                
                # Classify with confidence
                classification = self._classify_with_confidence(features, event_type)
                
                if classification['confidence'] > 0.3:  # Minimum confidence threshold
                    events.append({
                        'timestamp': df.iloc[peak_idx]['timestamp'],
                        'end_timestamp': df.iloc[event_end - 1]['timestamp'] if event_end > event_start else df.iloc[peak_idx]['timestamp'],
                        'event_type': classification['event_type'],
                        'severity': classification['severity'],
                        'confidence': classification['confidence'],
                        'peak_index': peak_idx,
                        'features': features,
                        'duration_seconds': len(event_segment) / self.SAMPLING_RATE
                    })
        
        return events
    
    def _extract_event_features(self, segment: pd.DataFrame, event_type: str) -> Dict:
        """Extract features from event segment for classification."""
        features = {
            'max_magnitude': segment['horizontal_magnitude_final'].max(),
            'min_magnitude': segment['horizontal_magnitude_final'].min(),
            'mean_jerk': segment['jerk_magnitude'].mean(),
            'max_jerk': segment['jerk_magnitude'].max(),
            'duration_samples': len(segment),
            'variance': segment['horizontal_magnitude_final'].var(),
        }
        
        if event_type == 'cornering':
            features['max_lateral_g'] = segment['lateral_g'].max()
        elif event_type == 'bumps':
            features['max_vertical_g'] = segment['vertical_g'].max()
            features['dominant_frequency'] = segment.get('dominant_frequency', 0).mean()
        
        return features
    
    def _classify_with_confidence(self, features: Dict, event_type: str) -> Dict:
        """Classify event with confidence scoring using rule-based ML approach."""
        confidence = 0.0
        severity = 'low'
        final_event_type = event_type
        
        if event_type == 'braking':
            # Harsh braking classification
            if features['min_magnitude'] < self.HARSH_BRAKE_THRESHOLD:
                confidence = min(abs(features['min_magnitude'] - self.HARSH_BRAKE_THRESHOLD) / 3.0, 1.0)
                severity = 'high' if confidence > 0.7 else 'medium'
                final_event_type = 'harsh_braking'
            elif features['min_magnitude'] < self.MODERATE_BRAKE_THRESHOLD:
                confidence = min(abs(features['min_magnitude'] - self.MODERATE_BRAKE_THRESHOLD) / 1.5, 1.0)
                severity = 'medium'
                final_event_type = 'moderate_braking'
                
        elif event_type == 'acceleration':
            # Harsh acceleration classification
            if features['max_magnitude'] > self.HARSH_ACCEL_THRESHOLD:
                confidence = min((features['max_magnitude'] - self.HARSH_ACCEL_THRESHOLD) / 2.5, 1.0)
                severity = 'high' if confidence > 0.7 else 'medium'
                final_event_type = 'harsh_acceleration'
            elif features['max_magnitude'] > self.MODERATE_ACCEL_THRESHOLD:
                confidence = min((features['max_magnitude'] - self.MODERATE_ACCEL_THRESHOLD) / 1.0, 1.0)
                severity = 'medium'
                final_event_type = 'moderate_acceleration'
                
        elif event_type == 'cornering':
            # Cornering detection
            if features['max_lateral_g'] > 1.5:
                confidence = min(features['max_lateral_g'] / 2.5, 1.0)
                severity = 'high' if confidence > 0.6 else 'medium'
                final_event_type = 'harsh_cornering'
            else:
                confidence = min(features['max_lateral_g'] / 1.5, 1.0)
                severity = 'low'
                final_event_type = 'moderate_cornering'
                
        elif event_type == 'bumps':
            # Bump detection
            if features['max_vertical_g'] > 2.5:
                confidence = min(features['max_vertical_g'] / 4.0, 1.0)
                severity = 'medium'
                final_event_type = 'harsh_bump'
            else:
                confidence = min(features['max_vertical_g'] / 2.5, 1.0)
                severity = 'low'
                final_event_type = 'moderate_bump'
        
        # Boost confidence based on jerk (rate of change)
        jerk_boost = min(features['max_jerk'] / 10.0, 0.3)
        confidence = min(confidence + jerk_boost, 1.0)
        
        return {
            'event_type': final_event_type,
            'severity': severity,
            'confidence': confidence
        }
    
    def detect_events_advanced(self, df: pd.DataFrame) -> List[Dict]:
        """Advanced event detection with ML-inspired classification."""
        # Compute advanced features
        df = self.compute_advanced_features(df)
        
        # Apply advanced smoothing
        df = self.advanced_smoothing(df)
        
        # Detect peaks
        peaks = self.detect_peaks_advanced(df)
        
        # Classify events
        events = self.classify_events_ml_inspired(df, peaks)
        
        return events
    
    def analyze_accelerometer_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[Dict]]:
        """Complete analysis pipeline for accelerometer data."""
        # Compute magnitude
        df_processed = self.compute_advanced_features(df)
        
        # Apply advanced smoothing
        df_processed = self.advanced_smoothing(df_processed)
        
        # Detect peaks
        peaks = self.detect_peaks_advanced(df_processed)
        
        # Classify events
        events = self.classify_events_ml_inspired(df_processed, peaks)
        
        print(f"✓ Detected {len(events)} accelerometer events")
        
        return df_processed, events
