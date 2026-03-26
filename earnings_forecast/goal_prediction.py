"""
Goal Prediction Module
Predicts driver goal achievement and provides status classification.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum


class GoalStatus(Enum):
    """Driver goal status enumeration."""
    GOAL_ON_TRACK = "GOAL_ON_TRACK"
    GOAL_AT_RISK = "GOAL_AT_RISK"
    GOAL_LIKELY_MISSED = "GOAL_LIKELY_MISSED"
    GOAL_ALREADY_ACHIEVED = "GOAL_ALREADY_ACHIEVED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class GoalPredictor:
    """Predicts driver goal achievement and classifies status."""
    
    def __init__(self):
        # Status thresholds
        self.ON_TRACK_THRESHOLD = 0.8      # 80% confidence of achieving goal
        self.AT_RISK_THRESHOLD = 0.5        # 50% confidence of achieving goal
        self.MIN_HOURS_FOR_PREDICTION = 1.0  # Minimum hours needed for prediction
        
        # Time-based adjustments
        self.PEAK_HOURS_MULTIPLIER = 1.3    # Expected earnings multiplier during peak hours
        self.OFF_PEAK_HOURS_MULTIPLIER = 0.8 # Expected earnings multiplier during off-peak
        
        # Goal achievement parameters
        self.COLD_START_PROGRESS_RATE = 0.15 # 15% of goal expected in first hour for new drivers
        self.TYPICAL_DAILY_HOURS = 8.0       # Typical work day length
        
    def predict_goal_achievement(self, goals_df: pd.DataFrame, 
                                velocity_metrics: pd.DataFrame,
                                forecasts: pd.DataFrame) -> pd.DataFrame:
        """Predict goal achievement for all drivers."""
        results = []
        
        # Merge data sources
        merged_data = self._merge_goal_data(goals_df, velocity_metrics, forecasts)
        
        for _, row in merged_data.iterrows():
            prediction = self._predict_single_driver_goal(row)
            results.append(prediction)
        
        if results:
            return pd.DataFrame(results)
        else:
            return pd.DataFrame()
    
    def _merge_goal_data(self, goals_df: pd.DataFrame, 
                        velocity_metrics: pd.DataFrame,
                        forecasts: pd.DataFrame) -> pd.DataFrame:
        """Merge goal data with velocity metrics and forecasts."""
        # Start with goals
        merged = goals_df.copy()
        
        # Merge velocity metrics
        if not velocity_metrics.empty:
            merged = merged.merge(
                velocity_metrics,
                on='driver_id',
                how='left'
            )
        
        # Merge forecasts
        if not forecasts.empty:
            merged = merged.merge(
                forecasts,
                on='driver_id',
                how='left',
                suffixes=('', '_forecast')
            )
        
        return merged
    
    def _predict_single_driver_goal(self, driver_data: Dict) -> Dict:
        """Predict goal achievement for a single driver."""
        driver_id = driver_data['driver_id']
        daily_goal = driver_data['daily_goal']
        
        # Get current progress
        current_earnings = driver_data.get('current_earnings', 0)
        current_hours = driver_data.get('current_hours_worked', 0)
        
        # Calculate progress percentage
        progress_percentage = min(100.0, (current_earnings / daily_goal) * 100) if daily_goal > 0 else 0
        
        # Determine status and predictions
        if progress_percentage >= 100:
            status = GoalStatus.GOAL_ALREADY_ACHIEVED
            achievement_probability = 1.0
            estimated_completion_time = datetime.now()
        elif current_hours < self.MIN_HOURS_FOR_PREDICTION:
            status = GoalStatus.INSUFFICIENT_DATA
            achievement_probability = self._estimate_cold_start_probability(progress_percentage, current_hours)
            estimated_completion_time = None
        else:
            status, achievement_probability, estimated_completion_time = self._calculate_goal_status(
                driver_data, progress_percentage
            )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            status, progress_percentage, driver_data
        )
        
        return {
            'driver_id': driver_id,
            'daily_goal': daily_goal,
            'current_earnings': current_earnings,
            'current_hours_worked': current_hours,
            'progress_percentage': progress_percentage,
            'goal_status': status.value,
            'achievement_probability': achievement_probability,
            'estimated_completion_time': estimated_completion_time,
            'earnings_needed': max(0, daily_goal - current_earnings),
            'recommended_hours_remaining': self._calculate_needed_hours(
                daily_goal, current_earnings, driver_data
            ),
            'recommendations': recommendations,
            'last_updated': datetime.now()
        }
    
    def _calculate_goal_status(self, driver_data: Dict, 
                             progress_percentage: float) -> Tuple[GoalStatus, float, Optional[datetime]]:
        """Calculate goal status, probability, and estimated completion time."""
        current_earnings = driver_data.get('current_earnings', 0)
        current_hours = driver_data.get('current_hours_worked', 0)
        daily_goal = driver_data['daily_goal']
        
        # Get current velocity
        current_velocity = driver_data.get('current_velocity', 15.0)  # Default fallback
        avg_velocity = driver_data.get('avg_earnings_per_hour', current_velocity)
        
        # Calculate time-based factors
        hour_of_day = datetime.now().hour
        time_multiplier = self._get_time_multiplier(hour_of_day)
        
        # Adjust velocity based on time of day
        adjusted_velocity = avg_velocity * time_multiplier
        
        # Calculate remaining earnings needed
        earnings_needed = daily_goal - current_earnings
        
        # Estimate hours needed at current pace
        if adjusted_velocity > 0:
            hours_needed = earnings_needed / adjusted_velocity
        else:
            hours_needed = float('inf')
        
        # Calculate remaining work time in day
        remaining_work_hours = self._get_remaining_work_hours()
        
        # Calculate achievement probability
        if hours_needed <= remaining_work_hours:
            achievement_probability = min(1.0, remaining_work_hours / (hours_needed + 0.1))
        else:
            achievement_probability = max(0.0, remaining_work_hours / hours_needed)
        
        # Determine status
        if achievement_probability >= self.ON_TRACK_THRESHOLD:
            status = GoalStatus.GOAL_ON_TRACK
        elif achievement_probability >= self.AT_RISK_THRESHOLD:
            status = GoalStatus.GOAL_AT_RISK
        else:
            status = GoalStatus.GOAL_LIKELY_MISSED
        
        # Estimate completion time
        if achievement_probability > 0.5:
            estimated_completion = datetime.now() + timedelta(hours=hours_needed)
        else:
            estimated_completion = None
        
        return status, achievement_probability, estimated_completion
    
    def _estimate_cold_start_probability(self, progress_percentage: float, 
                                       hours_worked: float) -> float:
        """Estimate achievement probability for drivers with insufficient data."""
        # Expected progress at this point for a driver on track
        expected_progress = (hours_worked / self.TYPICAL_DAILY_HOURS) * 100
        
        # Compare actual vs expected progress
        progress_ratio = progress_percentage / expected_progress if expected_progress > 0 else 0
        
        # Adjust probability based on progress ratio
        if progress_ratio >= 1.2:
            return 0.9  # Well ahead of schedule
        elif progress_ratio >= 1.0:
            return 0.8  # On track
        elif progress_ratio >= 0.8:
            return 0.6  # Slightly behind
        elif progress_ratio >= 0.6:
            return 0.4  # Behind
        else:
            return 0.2  # Significantly behind
    
    def _get_time_multiplier(self, hour: int) -> float:
        """Get time-based earnings multiplier."""
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            return self.PEAK_HOURS_MULTIPLIER
        elif 20 <= hour <= 23:  # Evening
            return 1.1
        elif 10 <= hour <= 16:  # Daytime
            return 1.0
        else:  # Late night/early morning
            return self.OFF_PEAK_HOURS_MULTIPLIER
    
    def _get_remaining_work_hours(self) -> float:
        """Get remaining work hours in the day."""
        current_time = datetime.now()
        end_of_day = current_time.replace(hour=22, minute=0, second=0, microsecond=0)  # Assume 10 PM end
        
        if current_time > end_of_day:
            return 0.0
        else:
            return (end_of_day - current_time).total_seconds() / 3600
    
    def _calculate_needed_hours(self, daily_goal: float, current_earnings: float,
                              driver_data: Dict) -> float:
        """Calculate recommended hours needed to reach goal."""
        earnings_needed = max(0, daily_goal - current_earnings)
        
        # Use average velocity with time adjustment
        avg_velocity = driver_data.get('avg_earnings_per_hour', 15.0)
        hour_of_day = datetime.now().hour
        time_multiplier = self._get_time_multiplier(hour_of_day)
        adjusted_velocity = avg_velocity * time_multiplier
        
        if adjusted_velocity > 0:
            return earnings_needed / adjusted_velocity
        else:
            return float('inf')
    
    def _generate_recommendations(self, status: GoalStatus, progress_percentage: float,
                                driver_data: Dict) -> List[str]:
        """Generate personalized recommendations for the driver."""
        recommendations = []
        
        if status == GoalStatus.GOAL_ALREADY_ACHIEVED:
            recommendations.append("🎉 Congratulations! You've achieved your daily goal!")
            recommendations.append("Consider taking a well-deserved break or continue earning for bonus rewards.")
            
        elif status == GoalStatus.GOAL_ON_TRACK:
            recommendations.append("✅ You're on track to reach your daily goal!")
            recommendations.append("Maintain your current pace and focus on high-demand areas.")
            
        elif status == GoalStatus.GOAL_AT_RISK:
            recommendations.append("⚠️ You're at risk of missing your daily goal.")
            recommendations.append("Consider driving during peak hours for higher earnings.")
            if progress_percentage < 50:
                recommendations.append("Focus on completing longer trips or surge areas.")
            
        elif status == GoalStatus.GOAL_LIKELY_MISSED:
            recommendations.append("❌ You're likely to miss your daily goal at current pace.")
            recommendations.append("Significantly increase driving time or target high-demand zones.")
            recommendations.append("Consider adjusting your goal for today and planning for tomorrow.")
            
        elif status == GoalStatus.INSUFFICIENT_DATA:
            recommendations.append("📊 Keep driving to get more accurate goal predictions.")
            recommendations.append("Focus on maintaining consistent driving patterns.")
        
        # Add velocity-specific recommendations
        current_velocity = driver_data.get('current_velocity', 0)
        avg_velocity = driver_data.get('avg_earnings_per_hour', 0)
        
        if current_velocity < avg_velocity * 0.8:
            recommendations.append("Your current earnings pace is below average. Consider changing locations or times.")
        elif current_velocity > avg_velocity * 1.2:
            recommendations.append("Great pace! You're earning above your average rate.")
        
        return recommendations
    
    def calculate_goal_metrics(self, predictions: pd.DataFrame) -> Dict:
        """Calculate overall goal achievement metrics."""
        if predictions.empty:
            return {}
        
        # Status distribution
        status_counts = predictions['goal_status'].value_counts().to_dict()
        
        # Progress metrics
        avg_progress = predictions['progress_percentage'].mean()
        median_progress = predictions['progress_percentage'].median()
        
        # Achievement probability
        avg_probability = predictions['achievement_probability'].mean()
        
        # Drivers on track
        on_track_count = len(predictions[
            predictions['goal_status'] == GoalStatus.GOAL_ON_TRACK.value
        ])
        
        # Drivers who already achieved goals
        achieved_count = len(predictions[
            predictions['goal_status'] == GoalStatus.GOAL_ALREADY_ACHIEVED.value
        ])
        
        return {
            'total_drivers': len(predictions),
            'status_distribution': status_counts,
            'average_progress_percentage': avg_progress,
            'median_progress_percentage': median_progress,
            'average_achievement_probability': avg_probability,
            'drivers_on_track': on_track_count,
            'drivers_achieved_goal': achieved_count,
            'goal_achievement_rate': achieved_count / len(predictions) if len(predictions) > 0 else 0
        }
