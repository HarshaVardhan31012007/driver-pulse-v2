"""
Event Patterns Page - Analysis of driver events and patterns
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config

# Import dashboard class
from app import DriverPulseDashboard

def main():
    """Event patterns page with detailed event analysis."""
    
    # Page header
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(220, 53, 69, 0.3);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            ⚡ Event Patterns
        </h1>
        <p style="
            color: rgba(255,255,255,0.95);
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
        ">
            Comprehensive analysis of driver events, patterns, and safety incidents
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = DriverPulseDashboard()
    
    # Sidebar filters
    st.sidebar.markdown('### 🎛️ Event Filters')
    
    # Time range filter
    time_range = st.sidebar.selectbox(
        'Time Range:',
        ['All Time', 'Last 24 Hours', 'Last 7 Days', 'Last 30 Days']
    )
    
    # Event type filter
    event_types = ['All Events', 'Hard Brake', 'Hard Acceleration', 'Speeding', 'Phone Usage', 'Stress Event']
    selected_event_type = st.sidebar.selectbox('Event Type:', event_types)
    
    # Severity filter
    severity_levels = ['All Severities', 'High', 'Medium', 'Low']
    selected_severity = st.sidebar.selectbox('Severity:', severity_levels)
    
    # Driver filter
    if 'driver_metrics' in dashboard.data:
        drivers = ['All Drivers'] + sorted(dashboard.data['driver_metrics']['driver_id'].unique().tolist())
        selected_driver = st.sidebar.selectbox('Driver:', drivers)
    else:
        selected_driver = 'All Drivers'
    
    # Load and process event data
    if 'events' not in dashboard.data:
        st.error('No event data available.')
        return
    
    events = dashboard.data['events'].copy()

    # -------------------------------
    # FIX missing column names safely
    # -------------------------------

    # Fix driver_id
    if 'driver_id' not in events.columns:
        if 'driver' in events.columns:
            events.rename(columns={'driver': 'driver_id'}, inplace=True)
        else:
            events['driver_id'] = "unknown"

    # Fix event_type
    if 'event_type' not in events.columns:
        if 'event_label' in events.columns:
            events.rename(columns={'event_label': 'event_type'}, inplace=True)
        elif 'event' in events.columns:
            events.rename(columns={'event': 'event_type'}, inplace=True)
        elif 'type' in events.columns:
            events.rename(columns={'type': 'event_type'}, inplace=True)
        else:
            events['event_type'] = "unknown_event"

    # Fix severity
    if 'severity' not in events.columns:
        events['severity'] = "low"

    # Fix confidence
    if 'confidence' not in events.columns:
        events['confidence'] = 1.0
    
    # Convert timestamp
    events['timestamp'] = pd.to_datetime(events['timestamp'])
    
    # Apply filters
    if time_range != 'All Time':
        now = datetime.now()
        if time_range == 'Last 24 Hours':
            start_time = now - timedelta(hours=24)
        elif time_range == 'Last 7 Days':
            start_time = now - timedelta(days=7)
        elif time_range == 'Last 30 Days':
            start_time = now - timedelta(days=30)
        
        events = events[events['timestamp'] >= start_time]
    
    if selected_event_type != 'All Events':
        events = events[events['event_type'] == selected_event_type]
    
    if selected_severity != 'All Severities':
        events = events[events['severity'] == selected_severity.lower()]
    
    if selected_driver != 'All Drivers':
        events = events[events['driver_id'] == selected_driver]
    
    if events.empty:
        st.warning('No events match the selected filters.')
        return
    
    # Event overview
    st.markdown('### 📊 Event Overview')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = len(events)
        st.metric(
            label="⚡ Total Events",
            value=f"{total_events:,}",
            delta="Last 24h" if time_range == 'All Time' else "Selected period"
        )
    
    with col2:
        high_severity = len(events[events['severity'] == 'high'])
        st.metric(
            label="🔴 High Severity",
            value=f"{high_severity:,}",
            delta=f"{(high_severity/total_events*100):.1f}%" if total_events > 0 else "0%"
        )
    
    with col3:
        unique_drivers = events['driver_id'].nunique()
        st.metric(
            label="👥 Drivers Affected",
            value=f"{unique_drivers:,}",
            delta=f"of {dashboard.data['driver_metrics']['driver_id'].nunique()} total"
        )
    
    with col4:
        avg_confidence = events['confidence'].mean() if 'confidence' in events.columns else 0
        st.metric(
            label="📈 Avg Confidence",
            value=f"{avg_confidence:.2f}",
            delta="Detection quality"
        )
    
    # Event timeline
    st.markdown('### 📈 Event Timeline Analysis')
    
    # Prepare event data for timeline
    events['event_label'] = events['event_type'].str.replace('_', ' ').str.title()
    
    # Normalize confidence for size (ensure positive values)
    if 'confidence' in events.columns:
        confidence_min = events['confidence'].min()
        confidence_max = events['confidence'].max()
        if confidence_min < 0:
            confidence_normalized = ((events['confidence'] - confidence_min) / (confidence_max - confidence_min)) * 50 + 10
        else:
            confidence_normalized = events['confidence']
    else:
        confidence_normalized = [10] * len(events)
    
    fig_timeline = px.scatter(
        events,
        x='timestamp',
        y='event_label',
        color='severity',
        size=confidence_normalized,
        title='Event Timeline Analysis',
        labels={
            'timestamp': 'Time',
            'event_label': 'Event Type',
            'severity': 'Severity',
            'confidence': 'Confidence'
        },
        color_discrete_map={
            'high': '#dc3545',
            'medium': '#ffc107',
            'low': '#28a745'
        },
        height=500
    )
    
    fig_timeline.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        hovermode='closest'
    )
    
    st.plotly_chart(fig_timeline, width='stretch')
    
    # Event distribution analysis
    st.markdown('### 📊 Event Distribution Analysis')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Event type distribution
        event_counts = events['event_type'].value_counts()
        
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=event_counts.index.str.replace('_', ' ').str.title(),
                values=event_counts.values,
                hole=0.3,
                marker_colors=['#dc3545', '#ffc107', '#28a745', '#17a2b8', '#6f42c1', '#fd7e14']
            )
        ])
        
        fig_pie.update_layout(
            title='Event Type Distribution',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_pie, width='stretch')
    
    with col2:
        # Severity distribution
        severity_counts = events['severity'].value_counts()
        
        fig_bar = go.Figure(data=[
            go.Bar(
                x=severity_counts.index.str.title(),
                y=severity_counts.values,
                marker_color=['#dc3545', '#ffc107', '#28a745']
            )
        ])
        
        fig_bar.update_layout(
            title='Severity Distribution',
            xaxis_title='Severity Level',
            yaxis_title='Number of Events',
            height=400
        )
        
        st.plotly_chart(fig_bar, width='stretch')
    
    # Driver-specific event analysis
    st.markdown('### 👥 Driver Event Analysis')
    
    # Events by driver
    driver_events = events.groupby('driver_id').agg({
        'event_type': 'count',
        'severity': lambda x: (x == 'high').sum(),
        'confidence': 'mean'
    }).reset_index()
    
    driver_events.columns = ['Driver ID', 'Total Events', 'High Severity Events', 'Avg Confidence']
    driver_events = driver_events.sort_values('Total Events', ascending=False)
    
    # Top 10 drivers with most events
    top_drivers = driver_events.head(10)
    
    fig_driver_events = px.bar(
        top_drivers,
        x='Driver ID',
        y='Total Events',
        color='High Severity Events',
        title='Top 10 Drivers by Event Count',
        labels={
            'Driver ID': 'Driver',
            'Total Events': 'Total Events',
            'High Severity Events': 'High Severity Count'
        },
        color_continuous_scale='Reds',
        height=400
    )
    
    st.plotly_chart(fig_driver_events, width='stretch')
    
    # Detailed events table
    st.markdown('### 📋 Detailed Event Log')
    
    # Prepare display data
    display_events = events.copy()
    display_events = display_events.sort_values('timestamp', ascending=False).head(100)
    
    display_columns = ['timestamp', 'driver_id', 'event_type', 'severity', 'confidence']
    if 'location' in display_events.columns:
        display_columns.append('location')
    
    display_events = display_events[display_columns].copy()
    display_events.columns = [col.replace('_', ' ').title() for col in display_columns]
    display_events['Timestamp'] = display_events['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format confidence
    if 'Confidence' in display_events.columns:
        display_events['Confidence'] = display_events['Confidence'].round(2)
    
    st.dataframe(display_events, width='stretch')
    
    # Pattern analysis
    st.markdown('### 🔍 Pattern Analysis & Insights')
    
    # Time-based patterns
    events['hour'] = events['timestamp'].dt.hour
    events['day_of_week'] = events['timestamp'].dt.day_name()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly pattern
        hourly_events = events.groupby('hour')['event_type'].count().reset_index()
        
        fig_hourly = px.line(
            hourly_events,
            x='hour',
            y='event_type',
            title='Events by Hour of Day',
            labels={'hour': 'Hour', 'event_type': 'Number of Events'},
            markers=True,
            color_discrete_sequence=['#dc3545']
        )
        
        fig_hourly.update_layout(height=300)
        st.plotly_chart(fig_hourly, width='stretch')
    
    with col2:
        # Day of week pattern
        daily_events = events.groupby('day_of_week')['event_type'].count().reset_index()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_events['day_of_week'] = pd.Categorical(daily_events['day_of_week'], categories=day_order, ordered=True)
        daily_events = daily_events.sort_values('day_of_week')
        
        fig_daily = px.bar(
            daily_events,
            x='day_of_week',
            y='event_type',
            title='Events by Day of Week',
            labels={'day_of_week': 'Day', 'event_type': 'Number of Events'},
            color_discrete_sequence=['#17a2b8']
        )
        
        fig_daily.update_layout(height=300)
        st.plotly_chart(fig_daily, width='stretch')
    
    # Safety recommendations
    st.markdown('### 🛡️ Safety Recommendations')
    
    # Generate insights based on patterns
    insights = []
    
    # Peak event hours
    if len(hourly_events) > 0:
        peak_hour = hourly_events.loc[hourly_events['event_type'].idxmax(), 'hour']
        insights.append({
            'type': 'Peak Risk Time',
            'message': f"Most events occur between {peak_hour}:00-{peak_hour+1}:00. Consider increased monitoring during this period.",
            'priority': 'High' if hourly_events['event_type'].max() > len(events) * 0.15 else 'Medium'
        })
    
    # High severity events
    high_severity_count = len(events[events['severity'] == 'high'])
    if high_severity_count > 0:
        insights.append({
            'type': 'High Severity Events',
            'message': f"{high_severity_count} high-severity events detected. Immediate review recommended for affected drivers.",
            'priority': 'High'
        })
    
    # Repeat offenders
    repeat_drivers = driver_events[driver_events['Total Events'] > driver_events['Total Events'].quantile(0.8)]
    if len(repeat_drivers) > 0:
        insights.append({
            'type': 'Repeat Offenders',
            'message': f"{len(repeat_drivers)} drivers have event counts in the top 20%. Consider targeted coaching for these drivers.",
            'priority': 'Medium'
        })
    
    # Most common event type
    most_common = event_counts.index[0]
    insights.append({
        'type': 'Common Event Pattern',
        'message': f"'{most_common.replace('_', ' ').title()}' is the most common event type. Focus training on this specific behavior.",
        'priority': 'Medium'
    })
    
    # Display insights
    for insight in insights:
        priority_color = {
            'High': '#dc3545',
            'Medium': '#ffc107',
            'Low': '#28a745'
        }[insight['priority']]
        
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, {priority_color}22 0%, {priority_color}11 100%);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            border-left: 4px solid {priority_color};
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <h4 style="color: {priority_color}; margin: 0 0 0.5rem 0;">
                        {insight['type']}
                    </h4>
                    <p style="margin: 0; color: #495057; line-height: 1.5;">
                        {insight['message']}
                    </p>
                </div>
                <span style="
                    background: {priority_color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    font-weight: bold;
                    margin-left: 1rem;
                ">
                    {insight['priority']}
                </span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Export functionality
    st.markdown('### 📤 Export Event Data')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('📊 Download Event Report', type='primary'):
            # Create event report
            report_data = {
                'Report Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Time Range': time_range,
                'Event Type Filter': selected_event_type,
                'Severity Filter': selected_severity,
                'Driver Filter': selected_driver,
                'Total Events': len(events),
                'High Severity Events': high_severity_count,
                'Unique Drivers': unique_drivers,
                'Average Confidence': f"{avg_confidence:.2f}"
            }
            
            # Add event breakdown
            for event_type, count in event_counts.items():
                report_data[f'{event_type.replace("_", " ").title()} Events'] = count
            
            report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
            csv_data = report_df.to_csv(index=False)
            
            st.download_button(
                label='Download Event Report',
                data=csv_data,
                file_name=f'event_patterns_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    with col2:
        if st.button('📈 Download Raw Event Data', type='secondary'):
            # Export filtered events
            export_events = display_events.copy()
            csv_data = export_events.to_csv(index=False)
            
            st.download_button(
                label='Download Raw Events',
                data=csv_data,
                file_name=f'events_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )

if __name__ == "__main__":
    main()
