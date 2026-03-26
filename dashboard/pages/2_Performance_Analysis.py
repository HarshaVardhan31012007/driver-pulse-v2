"""
Performance Analysis Page - Detailed driver performance metrics and analytics
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
    """Performance analysis page with detailed metrics and charts."""
    
    # Page header
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(40, 167, 69, 0.3);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            📊 Performance Analysis
        </h1>
        <p style="
            color: rgba(255,255,255,0.95);
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
        ">
            Comprehensive driver performance metrics and insights
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = DriverPulseDashboard()
    
    # Interactive filters in sidebar
    st.sidebar.markdown('### 🎛️ Performance Filters')
    
    if 'driver_metrics' in dashboard.data:
        metrics = dashboard.data['driver_metrics']
        
        # Driver filter
        drivers = ['All Drivers'] + sorted(metrics['driver_id'].unique().tolist())
        selected_driver = st.sidebar.selectbox('Select Driver:', drivers)
        
        # Safety rating filter
        safety_ratings = ['All Ratings'] + sorted(metrics['safety_rating_mode'].unique().tolist())
        selected_rating = st.sidebar.selectbox('Safety Rating:', safety_ratings)
        
        # Performance threshold
        min_score = st.sidebar.slider('Minimum Overall Score:', 0, 100, 0)
        
        # Apply filters
        filtered_metrics = metrics.copy()
        
        if selected_driver != 'All Drivers':
            filtered_metrics = filtered_metrics[filtered_metrics['driver_id'] == selected_driver]
        
        if selected_rating != 'All Ratings':
            filtered_metrics = filtered_metrics[filtered_metrics['safety_rating_mode'] == selected_rating]
        
        filtered_metrics = filtered_metrics[filtered_metrics['overall_score'] >= min_score]
        
        if len(filtered_metrics) == 0:
            st.warning('No drivers match the selected filters. Please adjust your criteria.')
            return
        
        # Performance overview
        st.markdown('### 📈 Performance Overview')
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_earnings = filtered_metrics['earnings_per_hour'].mean()
            st.metric(
                label="💰 Avg Earnings/Hour",
                value=f"₹{avg_earnings * 83:.0f}",
                delta=f"vs overall: {avg_earnings - metrics['earnings_per_hour'].mean():.1f}"
            )
        
        with col2:
            avg_stress = filtered_metrics['stress_score_mean'].mean()
            st.metric(
                label="😰 Avg Stress Score",
                value=f"{avg_stress:.1f}",
                delta=f"vs overall: {avg_stress - metrics['stress_score_mean'].mean():.1f}"
            )
        
        with col3:
            avg_overall = filtered_metrics['overall_score'].mean()
            st.metric(
                label="⭐ Avg Overall Score",
                value=f"{avg_overall:.1f}",
                delta=f"vs overall: {avg_overall - metrics['overall_score'].mean():.1f}"
            )
        
        with col4:
            driver_count = len(filtered_metrics)
            st.metric(
                label="👥 Drivers Analyzed",
                value=driver_count,
                delta=f"of {len(metrics)} total"
            )
        
        # Main performance matrix
        st.markdown('### 🎯 Driver Performance Matrix')
        
        fig = px.scatter(
            filtered_metrics, 
            x='earnings_per_hour', 
            y='stress_score_mean',
            size='overall_score',
            color='safety_rating_mode',
            hover_name='driver_id',
            title='Performance vs Stress Analysis',
            labels={
                'earnings_per_hour': 'Earnings (₹/hour)',
                'stress_score_mean': 'Stress Score',
                'overall_score': 'Overall Score',
                'safety_rating_mode': 'Safety Rating'
            },
            color_discrete_map={
                'EXCELLENT': '#28a745',
                'GOOD': '#17a2b8', 
                'FAIR': '#ffc107',
                'POOR': '#dc3545'
            },
            height=500
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Performance distribution charts
        st.markdown('### 📊 Performance Distribution')
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Earnings distribution
            earnings_dist = dashboard.insights.get('earnings_distribution', {})
            if earnings_dist:
                fig_earnings = go.Figure(data=[
                    go.Bar(
                        x=list(earnings_dist.keys()), 
                        y=list(earnings_dist.values()),
                        marker_color='#28a745'
                    )
                ])
                fig_earnings.update_layout(
                    title='Earnings Distribution',
                    xaxis_title='Earnings Range (₹/hour)',
                    yaxis_title='Number of Drivers',
                    height=400
                )
                st.plotly_chart(fig_earnings, width='stretch')
        
        with col2:
            # Safety rating distribution
            safety_counts = filtered_metrics['safety_rating_mode'].value_counts()
            fig_safety = go.Figure(data=[
                go.Pie(
                    labels=safety_counts.index, 
                    values=safety_counts.values,
                    hole=0.3,
                    marker_colors=['#28a745', '#17a2b8', '#ffc107', '#dc3545']
                )
            ])
            fig_safety.update_layout(
                title='Safety Rating Distribution',
                height=400
            )
            st.plotly_chart(fig_safety, width='stretch')
        
        # Detailed performance table
        st.markdown('### 📋 Detailed Performance Metrics')
        
        # Prepare display data
        display_metrics = filtered_metrics[[
            'driver_id', 'overall_score', 'earnings_per_hour', 
            'stress_score_mean', 'safety_rating_mode'
        ]].copy()
        
        display_metrics.columns = [
            'Driver ID', 'Overall Score', 'Earnings (₹/hour)', 
            'Stress Score', 'Safety Rating'
        ]
        display_metrics['Earnings (₹/hour)'] = display_metrics['Earnings (₹/hour)'].apply(
            lambda x: f"₹{x * 83:.2f}"
        )
        
        # Sort by overall score
        display_metrics = display_metrics.sort_values('Overall Score', ascending=False)
        
        st.dataframe(display_metrics, width='stretch')
        
        # Performance insights
        st.markdown('### 💡 Performance Insights')
        
        # Top performers
        top_performers = filtered_metrics.nlargest(3, 'overall_score')
        st.markdown('#### 🏆 Top Performers')
        
        for i, driver in enumerate(top_performers.iterrows(), 1):
            _, driver_data = driver
            medal_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                border-left: 6px solid #1e7e34;
                box-shadow: 0 8px 25px rgba(40, 167, 69, 0.3);
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: -10px;
                    right: -10px;
                    font-size: 4rem;
                    opacity: 0.1;
                    transform: rotate(-15deg);
                ">
                    {medal_emoji}
                </div>
                <div style="
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: white;
                    margin-bottom: 0.5rem;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                ">
                    {medal_emoji} Driver {driver_data['driver_id']}
                </div>
                <div style="
                    color: rgba(255,255,255,0.95);
                    font-size: 1.1rem;
                    font-weight: 600;
                    line-height: 1.6;
                ">
                    <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 20px; margin-right: 0.5rem;">
                        Score: {driver_data['overall_score']:.1f}
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 20px; margin-right: 0.5rem;">
                        Earnings: ₹{driver_data['earnings_per_hour'] * 83:.0f}/hr
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 20px;">
                        Safety: {driver_data['safety_rating_mode']}
                    </span>
                </div>
            </div>
            ''', unsafe_allow_html=True)
        
        # Areas for improvement
        low_performers = filtered_metrics.nsmallest(3, 'overall_score')
        st.markdown('#### 📈 Areas for Improvement')
        
        for i, driver in enumerate(low_performers.iterrows(), 1):
            _, driver_data = driver
            improvement_emoji = "📊" if i == 1 else "📈" if i == 2 else "🎯"
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                padding: 1.5rem;
                border-radius: 15px;
                margin-bottom: 1rem;
                border-left: 6px solid #bd2130;
                box-shadow: 0 8px 25px rgba(220, 53, 69, 0.3);
                position: relative;
                overflow: hidden;
            ">
                <div style="
                    position: absolute;
                    top: -10px;
                    right: -10px;
                    font-size: 4rem;
                    opacity: 0.1;
                    transform: rotate(-15deg);
                ">
                    {improvement_emoji}
                </div>
                <div style="
                    font-size: 1.3rem;
                    font-weight: 700;
                    color: white;
                    margin-bottom: 0.5rem;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                ">
                    {improvement_emoji} Driver {driver_data['driver_id']}
                </div>
                <div style="
                    color: rgba(255,255,255,0.95);
                    font-size: 1.1rem;
                    font-weight: 600;
                    line-height: 1.6;
                ">
                    <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 20px; margin-right: 0.5rem;">
                        Score: {driver_data['overall_score']:.1f}
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 20px; margin-right: 0.5rem;">
                        Earnings: ₹{driver_data['earnings_per_hour'] * 83:.0f}/hr
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 0.3rem 0.6rem; border-radius: 20px;">
                        Safety: {driver_data['safety_rating_mode']}
                    </span>
                </div>
            </div>
            ''', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
