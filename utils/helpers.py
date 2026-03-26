"""
Helper Functions Module
Utility functions for data processing, visualization, and common operations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings


def setup_plotting_style():
    """Setup consistent plotting style."""
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    warnings.filterwarnings('ignore')


def calculate_time_statistics(timestamps: pd.Series) -> Dict[str, Any]:
    """Calculate comprehensive time-based statistics."""
    if timestamps.empty:
        return {}
    
    timestamps = pd.to_datetime(timestamps)
    
    stats = {
        'count': len(timestamps),
        'start_time': timestamps.min(),
        'end_time': timestamps.max(),
        'duration_hours': (timestamps.max() - timestamps.min()).total_seconds() / 3600,
        'avg_gap_minutes': timestamps.diff().dt.total_seconds().mean() / 60,
        'events_per_hour': len(timestamps) / max(1, (timestamps.max() - timestamps.min()).total_seconds() / 3600)
    }
    
    # Hourly distribution
    stats['hourly_distribution'] = timestamps.dt.hour.value_counts().to_dict()
    
    # Daily distribution
    stats['daily_distribution'] = timestamps.dt.day_name().value_counts().to_dict()
    
    return stats


def create_time_bins(timestamps: pd.Series, bin_size_minutes: int = 15) -> pd.Series:
    """Create time bins for temporal aggregation."""
    timestamps = pd.to_datetime(timestamps)
    return timestamps.dt.floor(f'{bin_size_minutes}min')


def smooth_time_series(data: pd.Series, window: int = 5, method: str = 'rolling') -> pd.Series:
    """Apply smoothing to time series data."""
    if method == 'rolling':
        return data.rolling(window=window, center=True, min_periods=1).mean()
    elif method == 'ewm':
        return data.ewm(span=window, adjust=False).mean()
    elif method == 'savgol':
        from scipy import signal
        if len(data) >= window:
            return pd.Series(
                signal.savgol_filter(data, window_length=window, polyorder=3),
                index=data.index
            )
    return data


def detect_outliers_iqr(data: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Detect outliers using IQR method."""
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (data < lower_bound) | (data > upper_bound)


def calculate_percentile_ranks(data: pd.Series) -> pd.Series:
    """Calculate percentile ranks for data."""
    return data.rank(pct=True)


def create_confidence_intervals(data: pd.Series, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate confidence intervals for data."""
    alpha = 1 - confidence
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(data, lower_percentile)
    upper_bound = np.percentile(data, upper_percentile)
    
    return lower_bound, upper_bound


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_currency(amount: float, currency: str = '$') -> str:
    """Format currency amount."""
    return f"{currency}{amount:.2f}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format percentage value."""
    return f"{value:.{decimal_places}f}%"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0:
        return default
    return numerator / denominator


def merge_time_series_data(dfs: List[pd.DataFrame], 
                          timestamp_col: str = 'timestamp',
                          how: str = 'outer') -> pd.DataFrame:
    """Merge multiple time series DataFrames on timestamp."""
    if not dfs:
        return pd.DataFrame()
    
    merged = dfs[0].copy()
    
    for df in dfs[1:]:
        merged = pd.merge(
            merged, 
            df, 
            on=timestamp_col, 
            how=how,
            suffixes=('', '_dup')
        )
        
        # Remove duplicate columns
        dup_cols = [col for col in merged.columns if col.endswith('_dup')]
        merged = merged.drop(columns=dup_cols)
    
    return merged.sort_values(timestamp_col)


def resample_time_series(df: pd.DataFrame, 
                        timestamp_col: str = 'timestamp',
                        rule: str = '1min',
                        aggregation: Dict[str, str] = None) -> pd.DataFrame:
    """Resample time series data to different frequency."""
    if aggregation is None:
        aggregation = {col: 'mean' for col in df.select_dtypes(include=[np.number]).columns}
    
    df_resampled = df.set_index(timestamp_col).resample(rule).agg(aggregation)
    
    return df_resampled.reset_index()


def create_event_heatmap(events_df: pd.DataFrame, 
                        timestamp_col: str = 'timestamp',
                        value_col: str = 'confidence') -> go.Figure:
    """Create heatmap of events over time."""
    if events_df.empty:
        return go.Figure()
    
    # Extract hour and day of week
    events_df = events_df.copy()
    events_df['hour'] = pd.to_datetime(events_df[timestamp_col]).dt.hour
    events_df['day_of_week'] = pd.to_datetime(events_df[timestamp_col]).dt.day_name()
    
    # Create pivot table
    pivot_table = events_df.pivot_table(
        values=value_col,
        index='day_of_week',
        columns='hour',
        aggfunc='mean',
        fill_value=0
    )
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot_table = pivot_table.reindex(day_order)
    
    fig = px.imshow(
        pivot_table,
        title='Event Heatmap by Day and Hour',
        labels=dict(x="Hour of Day", y="Day of Week", color=value_col),
        color_continuous_scale='Viridis'
    )
    
    return fig


def create_event_timeline(events_df: pd.DataFrame,
                         timestamp_col: str = 'timestamp',
                         event_type_col: str = 'event_type',
                         confidence_col: str = 'confidence') -> go.Figure:
    """Create timeline visualization of events."""
    if events_df.empty:
        return go.Figure()
    
    fig = px.scatter(
        events_df,
        x=timestamp_col,
        y=event_type_col,
        size=confidence_col,
        color=event_type_col,
        title='Event Timeline',
        labels={timestamp_col: 'Time', event_type_col: 'Event Type'},
        hover_data={confidence_col: ':.2f'}
    )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Event Type",
        height=600
    )
    
    return fig


def create_earnings_chart(earnings_df: pd.DataFrame,
                         timestamp_col: str = 'timestamp',
                         earnings_col: str = 'earnings',
                         driver_col: str = 'driver_id') -> go.Figure:
    """Create earnings over time chart."""
    if earnings_df.empty:
        return go.Figure()
    
    fig = px.line(
        earnings_df,
        x=timestamp_col,
        y=earnings_col,
        color=driver_col,
        title='Earnings Over Time',
        labels={timestamp_col: 'Time', earnings_col: 'Earnings ($)'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Earnings ($)",
        height=500
    )
    
    return fig


def create_velocity_chart(velocity_df: pd.DataFrame,
                         timestamp_col: str = 'timestamp',
                         velocity_col: str = 'earnings_per_hour',
                         driver_col: str = 'driver_id') -> go.Figure:
    """Create earnings velocity chart."""
    if velocity_df.empty:
        return go.Figure()
    
    fig = px.line(
        velocity_df,
        x=timestamp_col,
        y=velocity_col,
        color=driver_col,
        title='Earnings Velocity ($/hour)',
        labels={timestamp_col: 'Time', velocity_col: 'Velocity ($/hour)'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Velocity ($/hour)",
        height=500
    )
    
    return fig


def create_goal_progress_chart(goals_df: pd.DataFrame,
                             driver_col: str = 'driver_id',
                             progress_col: str = 'progress_percentage',
                             goal_col: str = 'daily_goal') -> go.Figure:
    """Create goal progress chart."""
    if goals_df.empty:
        return go.Figure()
    
    fig = px.bar(
        goals_df,
        x=driver_col,
        y=progress_col,
        title='Goal Progress by Driver',
        labels={driver_col: 'Driver', progress_col: 'Progress (%)'},
        color=progress_col,
        color_continuous_scale='RdYlGn'
    )
    
    fig.add_hline(
        y=100, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Goal (100%)"
    )
    
    fig.update_layout(
        xaxis_title="Driver",
        yaxis_title="Progress (%)",
        height=500
    )
    
    return fig


def calculate_correlation_matrix(df: pd.DataFrame, 
                                columns: List[str] = None) -> pd.DataFrame:
    """Calculate correlation matrix for specified columns."""
    if columns is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
    else:
        numeric_cols = [col for col in columns if col in df.columns and df[col].dtype in ['int64', 'float64']]
    
    if not numeric_cols:
        return pd.DataFrame()
    
    return df[numeric_cols].corr()


def create_correlation_heatmap(corr_matrix: pd.DataFrame) -> go.Figure:
    """Create correlation heatmap."""
    if corr_matrix.empty:
        return go.Figure()
    
    fig = px.imshow(
        corr_matrix,
        title='Feature Correlation Matrix',
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    
    return fig


def validate_data_quality(df: pd.DataFrame, 
                         required_columns: List[str] = None) -> Dict[str, Any]:
    """Validate data quality and return quality metrics."""
    if required_columns is None:
        required_columns = []
    
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_columns': [],
        'null_counts': df.isnull().sum().to_dict(),
        'duplicate_rows': df.duplicated().sum(),
        'data_types': df.dtypes.to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
    }
    
    # Check for required columns
    missing_cols = set(required_columns) - set(df.columns)
    quality_report['missing_columns'] = list(missing_cols)
    
    # Calculate null percentages
    quality_report['null_percentages'] = {
        col: (count / len(df)) * 100 
        for col, count in quality_report['null_counts'].items()
    }
    
    return quality_report


def export_data_with_timestamp(df: pd.DataFrame, 
                             base_filename: str,
                             output_dir: str = "./outputs",
                             format: str = 'csv') -> str:
    """Export DataFrame with timestamp in filename."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{base_filename}_{timestamp}.{format}"
    filepath = os.path.join(output_dir, filename)
    
    if format == 'csv':
        df.to_csv(filepath, index=False)
    elif format == 'json':
        df.to_json(filepath, orient='records', date_format='iso')
    elif format == 'parquet':
        df.to_parquet(filepath, index=False)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    return filepath


def load_sample_data_config() -> Dict[str, Dict]:
    """Get configuration for generating sample data."""
    return {
        'drivers': {
            'count': 10,
            'rating_range': (3.5, 5.0),
            'cities': ['San Francisco', 'New York', 'Chicago', 'Los Angeles', 'Boston']
        },
        'trips': {
            'count_per_driver': 20,
            'duration_range': (10, 120),  # minutes
            'fare_range': (5.0, 50.0),
            'date_range': 7  # days
        },
        'accelerometer': {
            'samples_per_trip': 50,
            'sampling_rate': 10,  # Hz
            'noise_level': 0.1
        },
        'audio': {
            'samples_per_trip': 20,
            'sampling_rate': 2,  # Hz
            'baseline_db': 60,
            'noise_range': (50, 95)
        },
        'goals': {
            'daily_goal_range': (100, 300)  # dollars
        },
        'earnings': {
            'updates_per_hour': 4,
            'earning_variance': 0.2
        }
    }
