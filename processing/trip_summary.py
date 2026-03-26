"""
Trip Summary Module
Generates comprehensive trip summaries with event correlations.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json


class TripSummarizer:
    """Generates detailed summaries for each trip."""
    
    def __init__(self):
        # Trip summary fields
        self.summary_fields = [
            'trip_id',
            'driver_id', 
            'start_time',
            'end_time',
            'duration_minutes',
            'fare',
            'earnings_per_minute',
            'total_events',
            'stress_events',
            'harsh_braking_events',
            'harsh_acceleration_events',
            'noise_events',
            'event_rate_per_hour',
            'stress_score',
            'safety_rating',
            'route_efficiency',
            'peak_hour_trip',
            'recommendations'
        ]
    
    def create_trip_summaries(self, trips_df: pd.DataFrame,
                             fused_events: List[Dict],
                             accel_events: List[Dict],
                             audio_events: List[Dict]) -> pd.DataFrame:
        """Create comprehensive summaries for all trips."""
        summaries = []
        
        # Convert events to DataFrames for easier processing
        fused_df = self._events_to_dataframe(fused_events)
        accel_df = self._events_to_dataframe(accel_events)
        audio_df = self._events_to_dataframe(audio_events)
        
        for _, trip in trips_df.iterrows():
            summary = self._create_single_trip_summary(
                trip, fused_df, accel_df, audio_df
            )
            summaries.append(summary)
        
        if summaries:
            summaries_df = pd.DataFrame(summaries)
            
            # Sort by start time
            summaries_df = summaries_df.sort_values('start_time').reset_index(drop=True)
            
            return summaries_df
        else:
            return pd.DataFrame(columns=self.summary_fields)
    
    def _events_to_dataframe(self, events: List[Dict]) -> pd.DataFrame:
        """Convert events list to DataFrame for easier processing."""
        if not events:
            return pd.DataFrame()
        
        return pd.DataFrame(events)
    
    def _create_single_trip_summary(self, trip: pd.Series,
                                   fused_df: pd.DataFrame,
                                   accel_df: pd.DataFrame, 
                                   audio_df: pd.DataFrame) -> Dict:
        """Create summary for a single trip."""
        trip_start = trip['start_time']
        trip_end = trip['end_time']
        trip_id = trip['trip_id']
        driver_id = trip['driver_id']
        
        # Find events that occurred during this trip
        trip_fused_events = self._get_events_in_time_window(fused_df, trip_start, trip_end)
        trip_accel_events = self._get_events_in_time_window(accel_df, trip_start, trip_end)
        trip_audio_events = self._get_events_in_time_window(audio_df, trip_start, trip_end)
        
        # Calculate basic metrics
        duration_minutes = (trip_end - trip_start).total_seconds() / 60
        earnings_per_minute = trip['fare'] / duration_minutes if duration_minutes > 0 else 0
        
        # Count events by type
        total_events = len(trip_fused_events) + len(trip_accel_events) + len(trip_audio_events)
        stress_events = len(trip_fused_events)
        harsh_braking_events = len([e for e in trip_accel_events if 'braking' in e.get('event_type', '')])
        harsh_acceleration_events = len([e for e in trip_accel_events if 'acceleration' in e.get('event_type', '')])
        noise_events = len(trip_audio_events)
        
        # Calculate event rate
        event_rate_per_hour = (total_events / duration_minutes) * 60 if duration_minutes > 0 else 0
        
        # Calculate stress score
        stress_score = self._calculate_stress_score(
            trip_fused_events, trip_accel_events, trip_audio_events, duration_minutes
        )
        
        # Calculate safety rating
        safety_rating = self._calculate_safety_rating(stress_score, total_events, duration_minutes)
        
        # Determine if peak hour trip
        peak_hour_trip = self._is_peak_hour(trip_start)
        
        # Calculate route efficiency (simplified)
        route_efficiency = self._calculate_route_efficiency(earnings_per_minute, stress_score)
        
        # Generate recommendations
        recommendations = self._generate_trip_recommendations(
            stress_score, safety_rating, event_rate_per_hour, peak_hour_trip, earnings_per_minute
        )
        
        summary = {
            'trip_id': trip_id,
            'driver_id': driver_id,
            'start_time': trip_start,
            'end_time': trip_end,
            'duration_minutes': duration_minutes,
            'fare': trip['fare'],
            'earnings_per_minute': earnings_per_minute,
            'total_events': total_events,
            'stress_events': stress_events,
            'harsh_braking_events': harsh_braking_events,
            'harsh_acceleration_events': harsh_acceleration_events,
            'noise_events': noise_events,
            'event_rate_per_hour': event_rate_per_hour,
            'stress_score': stress_score,
            'safety_rating': safety_rating,
            'route_efficiency': route_efficiency,
            'peak_hour_trip': peak_hour_trip,
            'recommendations': json.dumps(recommendations)
        }
        
        return summary
    
    def _get_events_in_time_window(self, events_df: pd.DataFrame,
                                  start_time: datetime, 
                                  end_time: datetime) -> List[Dict]:
        """Get events that occurred within the specified time window."""
        if events_df.empty:
            return []
        
        # Filter events within trip time window
        mask = (
            (events_df['timestamp'] >= start_time) &
            (events_df['timestamp'] <= end_time)
        )
        
        filtered_events = events_df[mask]
        
        return filtered_events.to_dict('records')
    
    def _calculate_stress_score(self, fused_events: List[Dict],
                              accel_events: List[Dict],
                              audio_events: List[Dict],
                              duration_minutes: float) -> float:
        """Calculate overall stress score for the trip."""
        if duration_minutes == 0:
            return 0.0
        
        # Weight different event types
        stress_weights = {
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
        }
        
        total_stress = 0.0
        
        # Add stress from fused events
        for event in fused_events:
            stress_level = event.get('stress_level', 'low_stress')
            confidence = event.get('combined_confidence', 1.0)
            weight = stress_weights.get(stress_level, 1.0)
            total_stress += weight * confidence
        
        # Add stress from accelerometer events
        for event in accel_events:
            event_type = event.get('event_type', '')
            confidence = event.get('confidence', 1.0)
            weight = stress_weights.get(event_type, 1.0)
            total_stress += weight * confidence
        
        # Add stress from audio events
        for event in audio_events:
            event_type = event.get('event_type', '')
            confidence = event.get('confidence', 1.0)
            weight = stress_weights.get(event_type, 1.0)
            total_stress += weight * confidence
        
        # Normalize by trip duration (stress per minute)
        stress_score = total_stress / duration_minutes
        
        # Cap the score at 10 for interpretability
        return min(10.0, stress_score)
    
    def _calculate_safety_rating(self, stress_score: float, 
                               total_events: int, 
                               duration_minutes: float) -> str:
        """Calculate safety rating based on stress and events."""
        if total_events == 0:
            return 'EXCELLENT'
        
        # Safety rating criteria
        if stress_score <= 1.0 and total_events <= 2:
            return 'EXCELLENT'
        elif stress_score <= 2.5 and total_events <= 5:
            return 'GOOD'
        elif stress_score <= 5.0 and total_events <= 10:
            return 'FAIR'
        elif stress_score <= 8.0:
            return 'POOR'
        else:
            return 'CRITICAL'
    
    def _is_peak_hour(self, timestamp: datetime) -> bool:
        """Determine if trip occurred during peak hours."""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Weekday peak hours
        if day_of_week < 5:  # Monday-Friday
            if (7 <= hour <= 9) or (17 <= hour <= 19):
                return True
        
        # Weekend peak hours
        else:
            if 10 <= hour <= 22:
                return True
        
        return False
    
    def _calculate_route_efficiency(self, earnings_per_minute: float,
                                   stress_score: float) -> float:
        """Calculate route efficiency score."""
        # Higher earnings per minute and lower stress = higher efficiency
        if earnings_per_minute == 0:
            return 0.0
        
        # Normalize earnings per minute (assuming $0.50 to $2.00 per minute range)
        earnings_score = min(1.0, max(0.0, (earnings_per_minute - 0.5) / 1.5))
        
        # Stress penalty (higher stress reduces efficiency)
        stress_penalty = min(0.5, stress_score / 10.0)
        
        efficiency = earnings_score * (1.0 - stress_penalty)
        
        return round(efficiency, 2)
    
    def _generate_trip_recommendations(self, stress_score: float,
                                     safety_rating: str,
                                     event_rate_per_hour: float,
                                     peak_hour_trip: bool,
                                     earnings_per_minute: float) -> List[str]:
        """Generate personalized recommendations for the trip."""
        recommendations = []
        
        # Safety-based recommendations
        if safety_rating == 'CRITICAL':
            recommendations.append("🚨 Critical safety issues detected. Consider reviewing driving routes and habits.")
            recommendations.append("Take a break before next trip and review harsh braking/acceleration events.")
        elif safety_rating == 'POOR':
            recommendations.append("⚠️ Safety concerns detected. Focus on smoother driving techniques.")
            recommendations.append("Reduce speed and increase following distance to prevent harsh braking.")
        elif safety_rating == 'FAIR':
            recommendations.append("📊 Room for safety improvement. Monitor driving patterns during busy periods.")
        elif safety_rating in ['GOOD', 'EXCELLENT']:
            recommendations.append("✅ Excellent safety performance! Keep up the smooth driving.")
        
        # Stress-based recommendations
        if stress_score > 7.0:
            recommendations.append("😰 High stress detected. Consider less congested routes or off-peak hours.")
        elif stress_score > 4.0:
            recommendations.append("🧘 Moderate stress levels. Practice defensive driving techniques.")
        
        # Event rate recommendations
        if event_rate_per_hour > 10:
            recommendations.append("📈 High event rate detected. Focus on anticipating traffic flow.")
        elif event_rate_per_hour > 5:
            recommendations.append("👀 Moderate event rate. Increase situational awareness.")
        
        # Peak hour recommendations
        if peak_hour_trip and stress_score > 3.0:
            recommendations.append("🕐 Consider alternative routes during peak hours to reduce stress.")
        elif not peak_hour_trip and earnings_per_minute < 0.5:
            recommendations.append("💰 Consider driving during peak hours for higher earnings potential.")
        
        # Route efficiency recommendations
        if stress_score < 2.0 and event_rate_per_hour < 2:
            recommendations.append("🎯 Excellent route efficiency! Consider similar routes for future trips.")
        
        return recommendations
    
    def create_driver_trip_summary(self, trip_summaries: pd.DataFrame,
                                 driver_id: str) -> Dict:
        """Create summary statistics for a specific driver."""
        driver_trips = trip_summaries[trip_summaries['driver_id'] == driver_id]
        
        if driver_trips.empty:
            return {}
        
        summary = {
            'driver_id': driver_id,
            'total_trips': len(driver_trips),
            'total_earnings': driver_trips['fare'].sum(),
            'total_duration_hours': driver_trips['duration_minutes'].sum() / 60,
            'avg_earnings_per_trip': driver_trips['fare'].mean(),
            'avg_earnings_per_hour': driver_trips['fare'].sum() / (driver_trips['duration_minutes'].sum() / 60),
            'total_events': driver_trips['total_events'].sum(),
            'total_stress_events': driver_trips['stress_events'].sum(),
            'avg_stress_score': driver_trips['stress_score'].mean(),
            'safety_rating_distribution': driver_trips['safety_rating'].value_counts().to_dict(),
            'peak_hour_trips': driver_trips['peak_hour_trip'].sum(),
            'avg_route_efficiency': driver_trips['route_efficiency'].mean(),
            'harsh_braking_total': driver_trips['harsh_braking_events'].sum(),
            'harsh_acceleration_total': driver_trips['harsh_acceleration_events'].sum()
        }
        
        return summary
    
    def save_trip_summaries(self, summaries_df: pd.DataFrame, 
                           output_path: str = "./outputs/trip_summaries.csv"):
        """Save trip summaries to file."""
        summaries_df.to_csv(output_path, index=False)
        print(f"✓ Saved {len(summaries_df)} trip summaries to {output_path}")
        
        return output_path
