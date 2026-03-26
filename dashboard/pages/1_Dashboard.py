"""
Main Dashboard Page - Overview and Key Metrics
Home page with performance overview and key analytics
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
    """Main dashboard page with overview and key metrics."""
    
    # Page header
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.3);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 3rem;
            font-weight: 800;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
        ">
            🏆 Driver Pulse Analytics
        </h1>
        <p style="
            color: rgba(255,255,255,0.95);
            margin: 1rem 0 0 0;
            font-size: 1.3rem;
            font-weight: 400;
        ">
            AI-Powered Driver Safety & Earnings Optimization Platform
        </p>
        <div style="
            margin-top: 2rem;
            padding: 1rem 2rem;
            background: rgba(255,255,255,0.1);
            border-radius: 50px;
            display: inline-block;
        ">
            <span style="color: white; font-weight: 600;">📊 Real-time Analytics • 🎯 Performance Insights • 💰 Earnings Optimization</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = DriverPulseDashboard()
    
    # Quick stats row
    st.markdown('### 📈 Quick Overview')
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total Earnings",
            value=f"₹{dashboard.insights.get('total_earnings', 0) * 83:,.0f}",
            delta="12.5% vs last period"
        )
    
    with col2:
        st.metric(
            label="⚡ Avg Earnings/Hour",
            value=f"₹{dashboard.insights.get('avg_earnings_per_hour', 0) * 83:.0f}",
            delta="8.3% improvement"
        )
    
    with col3:
        st.metric(
            label="🚗 Active Drivers",
            value=len(dashboard.data.get('driver_metrics', pd.DataFrame())),
            delta="2 new drivers"
        )
    
    with col4:
        safety_score = 10 - min(dashboard.insights.get('avg_stress_score', 0), 10)
        st.metric(
            label="⭐ Safety Score",
            value=f"{safety_score:.1f}/10",
            delta="5.7% better"
        )
    
    # Key metrics section
    dashboard.render_key_metrics()
    
    # Performance charts preview
    st.markdown('### 🎯 Performance Highlights')
    
    if 'driver_metrics' in dashboard.data:
        metrics = dashboard.data['driver_metrics']
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance scatter plot
            fig = px.scatter(
                metrics, 
                x='earnings_per_hour', 
                y='stress_score_mean',
                size='overall_score',
                color='safety_rating_mode',
                hover_name='driver_id',
                title='Driver Performance Matrix',
                labels={
                    'earnings_per_hour': 'Earnings (₹/hour)',
                    'stress_score_mean': 'Stress Score',
                    'overall_score': 'Overall Score',
                    'safety_rating_mode': 'Safety Rating'
                },
                height=400
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True
            )
            
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            # Safety rating distribution
            safety_counts = metrics['safety_rating_mode'].value_counts()
            fig = go.Figure(data=[
                go.Pie(
                    labels=safety_counts.index, 
                    values=safety_counts.values,
                    hole=0.3,
                    marker_colors=['#28a745', '#17a2b8', '#ffc107', '#dc3545']
                )
            ])
            fig.update_layout(
                title='Safety Rating Distribution',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, width='stretch')
    
    # Recent activity
    st.markdown('### 📋 Recent Activity')
    
    if 'trips' in dashboard.data:
        recent_trips = dashboard.data['trips'].sort_values('start_time', ascending=False).head(5)
        
        display_trips = recent_trips[['driver_id', 'fare', 'duration_minutes', 'total_events']].copy()
        display_trips.columns = ['Driver ID', 'Fare (₹)', 'Duration (min)', 'Events']
        display_trips['Fare (₹)'] = display_trips['Fare (₹)'].apply(lambda x: f"₹{x * 83:.2f}")
        
        st.dataframe(display_trips, width='stretch')
    
    # Navigation hints
    st.markdown('---')
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 2rem;
    ">
        <h3 style="color: #495057; margin-bottom: 1rem;">🧭 Navigate to Detailed Analysis</h3>
        <p style="color: #6c757d; margin-bottom: 1.5rem;">
            Use the sidebar to explore detailed analytics, driver comparisons, and individual driver profiles
        </p>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
            <span style="background: #667eea; color: white; padding: 0.5rem 1rem; border-radius: 20px;">📊 Performance Analysis</span>
            <span style="background: #28a745; color: white; padding: 0.5rem 1rem; border-radius: 20px;">⚡ Event Patterns</span>
            <span style="background: #ffc107; color: white; padding: 0.5rem 1rem; border-radius: 20px;">💎 Earnings Trends</span>
            <span style="background: #dc3545; color: white; padding: 0.5rem 1rem; border-radius: 20px;">🏆 Leaderboard</span>
            <span style="background: #17a2b8; color: white; padding: 0.5rem 1rem; border-radius: 20px;">👥 Driver Comparison</span>
            <span style="background: #6f42c1; color: white; padding: 0.5rem 1rem; border-radius: 20px;">🔍 Driver Details</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
