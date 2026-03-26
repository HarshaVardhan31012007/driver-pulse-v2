"""
Driver Details Page - Individual driver profiles and detailed analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    """Driver details page with individual driver analytics."""
    
    # Page header
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #6f42c1 0%, #5a32a3 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(111, 66, 193, 0.3);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            🔍 Driver Details
        </h1>
        <p style="
            color: rgba(255,255,255,0.95);
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
        ">
            Individual driver profiles and comprehensive performance analytics
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = DriverPulseDashboard()
    
    if 'driver_metrics' not in dashboard.data:
        st.error('No driver data available.')
        return
    
    metrics = dashboard.data['driver_metrics'].copy()
    
    # Driver selection
    st.markdown('### 👤 Select Driver')
    
    # Get available drivers
    available_drivers = sorted(metrics['driver_id'].unique().tolist())
    
    # Driver selection with search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_driver = st.selectbox(
            'Choose a driver to view details:',
            available_drivers,
            help='Select a driver to view their complete performance profile'
        )
    
    with col2:
        # Quick driver stats
        if selected_driver:
            driver_data = metrics[metrics['driver_id'] == selected_driver].iloc[0]
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #6f42c1 0%, #5a32a3 100%);
                padding: 1rem;
                border-radius: 10px;
                color: white;
                text-align: center;
            ">
                <div style="font-size: 1.5rem; font-weight: bold;">Driver {selected_driver}</div>
                <div style="font-size: 1.2rem;">Score: {driver_data['overall_score']:.1f}</div>
            </div>
            ''', unsafe_allow_html=True)
    
    if not selected_driver:
        st.info('Please select a driver to view their detailed profile.')
        return
    
    # Get driver data
    driver_data = metrics[metrics['driver_id'] == selected_driver].iloc[0]
    
    # Driver profile header
    st.markdown('### 📋 Driver Profile')
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Profile information
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 15px;
            border: 2px solid #6f42c1;
        ">
            <h3 style="color: #6f42c1; margin: 0 0 1rem 0; font-size: 1.5rem;">
                👤 Driver {selected_driver}
            </h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="color: #6c757d; font-size: 0.9rem;">Overall Score</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #495057;">{driver_data['overall_score']:.1f}/100</div>
                </div>
                <div>
                    <div style="color: #6c757d; font-size: 0.9rem;">Safety Rating</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #495057;">{driver_data['safety_rating_mode']}</div>
                </div>
                <div>
                    <div style="color: #6c757d; font-size: 0.9rem;">Earnings/Hour</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #28a745;">₹{driver_data['earnings_per_hour'] * 83:.0f}</div>
                </div>
                <div>
                    <div style="color: #6c757d; font-size: 0.9rem;">Stress Score</div>
                    <div style="font-size: 1.3rem; font-weight: bold; color: #dc3545;">{driver_data['stress_score_mean']:.1f}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        # Performance badge
        score = driver_data['overall_score']
        if score >= 80:
            badge_color = '#28a745'
            badge_text = 'Excellent'
            badge_icon = '🌟'
        elif score >= 60:
            badge_color = '#17a2b8'
            badge_text = 'Good'
            badge_icon = '👍'
        elif score >= 40:
            badge_color = '#ffc107'
            badge_text = 'Fair'
            badge_icon = '📈'
        else:
            badge_color = '#dc3545'
            badge_text = 'Needs Improvement'
            badge_icon = '📊'
        
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, {badge_color} 0%, {badge_color}dd 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        ">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{badge_icon}</div>
            <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                {badge_text}
            </div>
            <div style="font-size: 2rem; font-weight: bold;">
                {score:.0f}
            </div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                Performance Score
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        # Quick actions
        st.markdown('### 🚀 Quick Actions')
        
        if st.button('📊 View Full Analytics', type='primary', key='full_analytics'):
            st.session_state.show_full_analytics = True
        
        if st.button('📤 Download Report', type='secondary', key='download_report'):
            st.session_state.download_report = True
        
        if st.button('🔄 Refresh Data', key='refresh_data'):
            st.rerun()
    
    # Performance metrics deep dive
    st.markdown('### 📊 Performance Metrics')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = driver_data['overall_score'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Performance Score"},
            delta = {'reference': metrics['overall_score'].mean()},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#6f42c1"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "#6f42c1"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, width='stretch')
    
    with col2:
        # Skills radar chart
        skills_data = {
            'Earnings': (driver_data['earnings_per_hour'] / metrics['earnings_per_hour'].max()) * 100,
            'Safety': ((10 - driver_data['stress_score_mean']) / 10) * 100,
            'Consistency': (100 - driver_data['stress_score_mean']) * 10,
            'Efficiency': driver_data['overall_score']
        }
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=list(skills_data.values()),
            theta=list(skills_data.keys()),
            fill='toself',
            name=f'Driver {selected_driver}',
            line_color='#6f42c1',
            fillcolor='rgba(111, 66, 193, 0.25)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title="Driver Skills Assessment",
            height=300
        )
        
        st.plotly_chart(fig_radar, width='stretch')
    
    # Trip history and trends
    if 'trips' in dashboard.data:
        st.markdown('### 🚗 Trip History & Trends')
        
        trips = dashboard.data['trips'].copy()
        driver_trips = trips[trips['driver_id'] == selected_driver].copy()
        
        if not driver_trips.empty:
            # Time series of earnings
            driver_trips['date'] = pd.to_datetime(driver_trips['start_time']).dt.date
            daily_earnings = driver_trips.groupby('date').agg({
                'fare': 'sum',
                'earnings_per_minute': 'mean',
                'trip_id': 'count',
                'total_events': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Earnings trend
                fig_trend = px.line(
                    daily_earnings,
                    x='date',
                    y='fare',
                    title=f'Daily Earnings - Driver {selected_driver}',
                    labels={'fare': 'Earnings ($)', 'date': 'Date'},
                    color_discrete_sequence=['#6f42c1']
                )
                fig_trend.update_traces(line_width=3)
                fig_trend.update_layout(height=300)
                st.plotly_chart(fig_trend, width='stretch')
            
            with col2:
                # Trip performance
                fig_performance = px.scatter(
                    driver_trips,
                    x='duration_minutes',
                    y='fare',
                    size='total_events',
                    title=f'Trip Performance - Driver {selected_driver}',
                    labels={
                        'duration_minutes': 'Duration (min)',
                        'fare': 'Fare ($)',
                        'total_events': 'Events'
                    },
                    color_discrete_sequence=['#6f42c1']
                )
                fig_performance.update_layout(height=300)
                st.plotly_chart(fig_performance, width='stretch')
            
            # Recent trips table
            st.markdown('### 📋 Recent Trips')
            
            recent_trips = driver_trips.sort_values('start_time', ascending=False).head(10)
            
            display_trips = recent_trips[[
                'start_time', 'fare', 'duration_minutes', 
                'total_events', 'stress_score'
            ]].copy()
            
            display_trips.columns = [
                'Start Time', 'Fare ($)', 'Duration (min)', 
                'Events', 'Stress Score'
            ]
            display_trips['Fare ($)'] = display_trips['Fare ($)'].apply(
                lambda x: f"₹{x * 83:.2f}"
            )
            
            st.dataframe(display_trips, width='stretch')
    
    # Performance comparison with peers
    st.markdown('### 🏆 Performance vs Peers')
    
    # Calculate percentiles
    percentiles = {}
    for metric in ['overall_score', 'earnings_per_hour', 'stress_score_mean']:
        driver_value = driver_data[metric]
        total_drivers = len(metrics)
        better_count = len(metrics[metrics[metric] > driver_value])
        percentile = ((total_drivers - better_count) / total_drivers) * 100
        percentiles[metric] = percentile
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 2rem; font-weight: bold;">
                {percentiles['overall_score']:.0f}%
            </div>
            <div style="font-size: 0.9rem;">Overall Score Percentile</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 2rem; font-weight: bold;">
                {percentiles['earnings_per_hour']:.0f}%
            </div>
            <div style="font-size: 0.9rem;">Earnings Percentile</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        stress_percentile = 100 - percentiles['stress_score_mean']  # Lower stress is better
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            color: white;
        ">
            <div style="font-size: 2rem; font-weight: bold;">
                {stress_percentile:.0f}%
            </div>
            <div style="font-size: 0.9rem;">Low Stress Percentile</div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Recommendations
    st.markdown('### 💡 Performance Recommendations')
    
    recommendations = []
    
    # Generate recommendations based on performance
    if driver_data['overall_score'] < 50:
        recommendations.append({
            'priority': 'High',
            'category': 'Overall Performance',
            'recommendation': 'Focus on improving overall driving consistency and efficiency'
        })
    
    if driver_data['earnings_per_hour'] < metrics['earnings_per_hour'].quantile(0.5):
        recommendations.append({
            'priority': 'Medium',
            'category': 'Earnings',
            'recommendation': 'Optimize route planning and trip acceptance strategy'
        })
    
    if driver_data['stress_score_mean'] > metrics['stress_score_mean'].quantile(0.75):
        recommendations.append({
            'priority': 'High',
            'category': 'Stress Management',
            'recommendation': 'Consider stress reduction techniques and break scheduling'
        })
    
    if driver_data['safety_rating_mode'] in ['FAIR', 'POOR']:
        recommendations.append({
            'priority': 'High',
            'category': 'Safety',
            'recommendation': 'Review safety protocols and defensive driving practices'
        })
    
    if not recommendations:
        recommendations.append({
            'priority': 'Low',
            'category': 'General',
            'recommendation': 'Maintain current excellent performance levels'
        })
    
    # Display recommendations
    for rec in recommendations:
        priority_color = {
            'High': '#dc3545',
            'Medium': '#ffc107',
            'Low': '#28a745'
        }[rec['priority']]
        
        st.markdown(f'''
        <div style="
            background: linear-gradient(135deg, {priority_color}22 0%, {priority_color}11 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            border-left: 4px solid {priority_color};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{rec['category']}:</strong> {rec['recommendation']}
                </div>
                <span style="
                    background: {priority_color};
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.8rem;
                    font-weight: bold;
                ">
                    {rec['priority']}
                </span>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Export functionality
    st.markdown('### 📤 Export Driver Profile')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('📊 Download Full Report', type='primary', key='download_full'):
            # Create comprehensive report
            report_data = {
                'Driver ID': selected_driver,
                'Report Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'Overall Score': f"{driver_data['overall_score']:.2f}",
                'Earnings per Hour': f"₹{driver_data['earnings_per_hour'] * 83:.2f}",
                'Stress Score': f"{driver_data['stress_score_mean']:.2f}",
                'Safety Rating': driver_data['safety_rating_mode'],
                'Overall Percentile': f"{percentiles['overall_score']:.1f}%",
                'Earnings Percentile': f"{percentiles['earnings_per_hour']:.1f}%",
                'Low Stress Percentile': f"{stress_percentile:.1f}%"
            }
            
            # Add recommendations
            for i, rec in enumerate(recommendations, 1):
                report_data[f'Recommendation {i}'] = f"{rec['category']}: {rec['recommendation']}"
            
            report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
            csv_data = report_df.to_csv(index=False)
            
            st.download_button(
                label='Download Driver Report',
                data=csv_data,
                file_name=f'driver_{selected_driver}_profile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    with col2:
        if st.button('🔄 Compare with Another Driver', type='secondary'):
            # Redirect to comparison page with this driver pre-selected
            st.session_state.preselected_drivers = [selected_driver]
            st.info('Navigate to Driver Comparison page to compare with other drivers')

if __name__ == "__main__":
    main()
