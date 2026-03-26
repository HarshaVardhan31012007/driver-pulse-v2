"""
Earnings Velocity Model
Computes driver earning pace and velocity metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import warnings


class EarningsVelocityModel:
    """Models and forecasts driver earnings velocity."""
    
    def __init__(self):
        self.velocity_models = {}  # Store models for each driver
        self.scalers = {}  # Store scalers for each driver
        
        # Velocity calculation parameters
        self.MIN_HOURS_FOR_VELOCITY = 2.0  # Minimum hours needed for stable velocity
        self.VELOCITY_WINDOW_HOURS = 4.0    # Rolling window for velocity calculation
        self.COLD_START_VELOCITY = 15.0     # Default velocity for new drivers ($/hour)
        
        # Forecast parameters
        self.FORECAST_HORIZON_HOURS = 8.0   # Hours to forecast ahead
        self.MIN_DATA_POINTS = 5             # Minimum data points for modeling
        
    def calculate_earnings_velocity(self, earnings_log: pd.DataFrame, 
                                  trips: pd.DataFrame) -> pd.DataFrame:
        """Calculate earnings velocity for drivers."""
        # Merge earnings log with trips for context
        merged_data = self._merge_earnings_with_trips(earnings_log, trips)
        
        # Calculate time-based metrics
        velocity_data = []
        
        for driver_id in merged_data['driver_id'].unique():
            driver_data = merged_data[merged_data['driver_id'] == driver_id].copy()
            driver_data = driver_data.sort_values('timestamp')
            
            # Calculate cumulative earnings and time
            driver_data['cumulative_earnings'] = driver_data['earnings'].cumsum()
            driver_data['hours_elapsed'] = (
                driver_data['timestamp'] - driver_data['timestamp'].min()
            ).dt.total_seconds() / 3600
            
            # Calculate rolling velocity
            driver_data = self._calculate_rolling_velocity(driver_data)
            
            # Calculate trip-based velocity
            driver_data = self._calculate_trip_velocity(driver_data)
            
            velocity_data.append(driver_data)
        
        if velocity_data:
            return pd.concat(velocity_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def _merge_earnings_with_trips(self, earnings_log: pd.DataFrame, 
                                 trips: pd.DataFrame) -> pd.DataFrame:
        """Merge earnings log with trip data."""
        # Create time-based bins for earnings
        earnings_log = earnings_log.copy()
        earnings_log['time_bin'] = earnings_log['timestamp'].dt.floor('15min')  # 15-minute bins
        
        # Aggregate earnings by time bin and driver
        earnings_binned = earnings_log.groupby(['driver_id', 'time_bin']).agg({
            'earnings': 'sum'
        }).reset_index()
        earnings_binned['timestamp'] = earnings_binned['time_bin']
        
        # Merge with trip data for context
        # Since trips have start_time/end_time, we'll create a simple mapping
        # In a real system, you'd need more sophisticated time alignment
        return earnings_binned
    
    def _calculate_rolling_velocity(self, driver_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate rolling earnings velocity."""
        driver_data = driver_data.copy()
        
        # Calculate rolling earnings over time window
        window_size = int(self.VELOCITY_WINDOW_HOURS * 4)  # 4 bins per hour (15-min bins)
        
        driver_data['rolling_earnings'] = driver_data['earnings'].rolling(
            window=window_size, min_periods=1
        ).sum()
        
        driver_data['rolling_hours'] = driver_data['hours_elapsed'].rolling(
            window=window_size, min_periods=1
        ).apply(lambda x: x.max() - x.min() if len(x) > 1 else 0)
        
        # Calculate velocity (earnings per hour)
        driver_data['earnings_per_hour'] = np.where(
            driver_data['rolling_hours'] > 0,
            driver_data['rolling_earnings'] / driver_data['rolling_hours'],
            0
        )
        
        # Smooth velocity
        driver_data['earnings_per_hour_smooth'] = driver_data['earnings_per_hour'].rolling(
            window=3, min_periods=1, center=True
        ).mean()
        
        return driver_data
    
    def _calculate_trip_velocity(self, driver_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate trip-based velocity metrics."""
        driver_data = driver_data.copy()
        
        # Calculate trips per hour (simplified)
        driver_data['trips_per_hour'] = driver_data['earnings'] / np.where(
            driver_data['earnings'] > 0,
            driver_data['earnings'],  # This is a placeholder - would need actual trip counts
            1
        )
        
        return driver_data
    
    def build_velocity_models(self, velocity_data: pd.DataFrame) -> Dict[str, LinearRegression]:
        """Build velocity prediction models for each driver."""
        models = {}
        scalers = {}
        
        for driver_id in velocity_data['driver_id'].unique():
            driver_data = velocity_data[velocity_data['driver_id'] == driver_id].copy()
            
            if len(driver_data) < self.MIN_DATA_POINTS:
                continue
            
            # Prepare features for modeling
            X, y = self._prepare_model_features(driver_data)
            
            if X is None or len(X) < self.MIN_DATA_POINTS:
                continue
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Build model
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            models[driver_id] = model
            scalers[driver_id] = scaler
        
        self.velocity_models = models
        self.scalers = scalers
        
        print(f"✓ Built velocity models for {len(models)} drivers")
        return models
    
    def _prepare_model_features(self, driver_data: pd.DataFrame) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare features for velocity modeling."""
        # Feature engineering
        features = []
        target = []
        
        for i in range(2, len(driver_data)):
            # Time-based features
            hour_of_day = driver_data.iloc[i]['timestamp'].hour
            day_of_week = driver_data.iloc[i]['timestamp'].dayofweek
            
            # Historical features
            recent_velocity = driver_data.iloc[i-1]['earnings_per_hour_smooth']
            velocity_trend = (
                driver_data.iloc[i-1]['earnings_per_hour_smooth'] - 
                driver_data.iloc[i-2]['earnings_per_hour_smooth']
            )
            
            # Cumulative features
            hours_worked = driver_data.iloc[i]['hours_elapsed']
            cumulative_earnings = driver_data.iloc[i]['cumulative_earnings']
            
            feature_row = [
                hour_of_day,
                day_of_week,
                recent_velocity,
                velocity_trend,
                hours_worked,
                cumulative_earnings
            ]
            
            features.append(feature_row)
            target.append(driver_data.iloc[i]['earnings_per_hour_smooth'])
        
        if len(features) >= self.MIN_DATA_POINTS:
            return np.array(features), np.array(target)
        else:
            return None, None
    
    def forecast_earnings(self, velocity_data: pd.DataFrame, 
                         forecast_hours: float = None) -> pd.DataFrame:
        """Forecast future earnings for drivers."""
        if forecast_hours is None:
            forecast_hours = self.FORECAST_HORIZON_HOURS
        
        forecasts = []
        
        for driver_id in velocity_data['driver_id'].unique():
            driver_data = velocity_data[velocity_data['driver_id'] == driver_id].copy()
            driver_data = driver_data.sort_values('timestamp')
            
            if len(driver_data) == 0:
                continue
            
            # Get current state
            current_earnings = driver_data['cumulative_earnings'].iloc[-1]
            current_hours = driver_data['hours_elapsed'].iloc[-1]
            
            # Get current velocity
            if len(driver_data) >= 3:
                current_velocity = driver_data['earnings_per_hour_smooth'].iloc[-1]
            else:
                current_velocity = self.COLD_START_VELOCITY
            
            # Generate forecast
            forecast = self._generate_driver_forecast(
                driver_id, current_earnings, current_hours, 
                current_velocity, forecast_hours
            )
            
            forecasts.append(forecast)
        
        if forecasts:
            return pd.DataFrame(forecasts)
        else:
            return pd.DataFrame()
    
    def _generate_driver_forecast(self, driver_id: str, current_earnings: float,
                                current_hours: float, current_velocity: float,
                                forecast_hours: float) -> Dict:
        """Generate earnings forecast for a single driver."""
        # Simple linear forecast with adjustments
        forecast_earnings = current_earnings + (current_velocity * forecast_hours)
        
        # Add time-based adjustments
        current_time = datetime.now()
        hour_factor = self._get_hourly_factor(current_time.hour)
        
        # Adjust forecast based on time of day
        adjusted_forecast = forecast_earnings * hour_factor
        
        # Calculate confidence bounds
        confidence = min(0.9, max(0.3, len([driver_id]) / 10))  # Simplified confidence
        
        return {
            'driver_id': driver_id,
            'current_earnings': current_earnings,
            'current_hours_worked': current_hours,
            'current_velocity': current_velocity,
            'forecast_hours': forecast_hours,
            'forecast_earnings': adjusted_forecast,
            'forecast_confidence': confidence,
            'hourly_adjustment_factor': hour_factor
        }
    
    def _get_hourly_factor(self, hour: int) -> float:
        """Get hourly adjustment factor based on typical demand patterns."""
        # Simplified demand pattern (higher during rush hours, lower late night)
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Rush hours
            return 1.3
        elif 10 <= hour <= 16:  # Daytime
            return 1.1
        elif 20 <= hour <= 22:  # Evening
            return 1.2
        else:  # Late night/early morning
            return 0.8
    
    def calculate_velocity_metrics(self, velocity_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate summary velocity metrics for drivers."""
        metrics = []
        
        for driver_id in velocity_data['driver_id'].unique():
            driver_data = velocity_data[velocity_data['driver_id'] == driver_id]
            
            if len(driver_data) == 0:
                continue
            
            # Calculate metrics
            avg_velocity = driver_data['earnings_per_hour_smooth'].mean()
            max_velocity = driver_data['earnings_per_hour_smooth'].max()
            min_velocity = driver_data['earnings_per_hour_smooth'].min()
            
            # Velocity consistency (coefficient of variation)
            velocity_std = driver_data['earnings_per_hour_smooth'].std()
            velocity_consistency = 1 - (velocity_std / avg_velocity) if avg_velocity > 0 else 0
            
            # Recent trend
            if len(driver_data) >= 5:
                recent_velocity = driver_data['earnings_per_hour_smooth'].tail(3).mean()
                earlier_velocity = driver_data['earnings_per_hour_smooth'].head(3).mean()
                velocity_trend = (recent_velocity - earlier_velocity) / earlier_velocity if earlier_velocity > 0 else 0
            else:
                velocity_trend = 0
            
            metrics.append({
                'driver_id': driver_id,
                'avg_earnings_per_hour': avg_velocity,
                'max_earnings_per_hour': max_velocity,
                'min_earnings_per_hour': min_velocity,
                'velocity_consistency': velocity_consistency,
                'velocity_trend': velocity_trend,
                'total_hours_worked': driver_data['hours_elapsed'].max(),
                'total_earnings': driver_data['cumulative_earnings'].max()
            })
        
        return pd.DataFrame(metrics)
