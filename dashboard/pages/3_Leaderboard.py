"""
Leaderboard Page - Driver rankings and competitive performance metrics
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
    """Leaderboard page with driver rankings and competitive metrics."""
    
    # Page header
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #ffc107 0%, #ff6b6b 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(255, 193, 7, 0.3);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            🏆 Driver Leaderboard
        </h1>
        <p style="
            color: rgba(255,255,255,0.95);
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
        ">
            Real-time driver rankings and competitive performance metrics
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = DriverPulseDashboard()
    
    if 'driver_metrics' not in dashboard.data:
        st.error('No driver data available for leaderboard.')
        return
    
    metrics = dashboard.data['driver_metrics'].copy()
    
    # Sidebar filters
    st.sidebar.markdown('### 🎛️ Leaderboard Filters')
    
    # Ranking metric selection
    ranking_metric = st.sidebar.selectbox(
        'Rank by:',
        ['Overall Score', 'Earnings/Hour', 'Safety Score', 'Lowest Stress'],
        help='Choose the primary metric for ranking'
    )
    
    # Safety rating filter
    safety_filter = st.sidebar.selectbox(
        'Safety Rating:',
        ['All Ratings', 'EXCELLENT', 'GOOD', 'FAIR', 'POOR']
    )
    
    # Time period
    time_period = st.sidebar.selectbox(
        'Time Period:',
        ['All Time', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days']
    )
    
    # Apply filters
    filtered_metrics = metrics.copy()
    
    if safety_filter != 'All Ratings':
        filtered_metrics = filtered_metrics[filtered_metrics['safety_rating_mode'] == safety_filter]
    
    # Sort by selected metric
    if ranking_metric == 'Overall Score':
        filtered_metrics = filtered_metrics.sort_values('overall_score', ascending=False)
    elif ranking_metric == 'Earnings/Hour':
        filtered_metrics = filtered_metrics.sort_values('earnings_per_hour', ascending=False)
    elif ranking_metric == 'Safety Score':
        # Create safety score (inverse of stress)
        filtered_metrics['safety_score'] = 10 - filtered_metrics['stress_score_mean']
        filtered_metrics = filtered_metrics.sort_values('safety_score', ascending=False)
    elif ranking_metric == 'Lowest Stress':
        filtered_metrics = filtered_metrics.sort_values('stress_score_mean', ascending=True)
    
    # Top performers showcase
    st.markdown('### 🥇 Top Performers')
    
    # Get top 3 drivers
    top_3 = filtered_metrics.head(3)
    
    col1, col2, col3 = st.columns(3)
    
    medals = ['🥇', '🥈', '🥉']
    colors = ['#ffd700', '#c0c0c0', '#cd7f32']
    
    for i, (col, driver, medal, color) in enumerate(zip([col1, col2, col3], top_3.itertuples(), medals, colors)):
        with col:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                border: 2px solid {color};
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            ">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">{medal}</div>
                <h3 style="color: #495057; margin: 0.5rem 0;">Driver {driver.driver_id}</h3>
                <div style="font-size: 1.5rem; font-weight: bold; color: #28a745; margin: 0.5rem 0;">
                    {driver.overall_score:.1f}
                </div>
                <div style="color: #6c757d; font-size: 0.9rem;">Overall Score</div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #dee2e6;">
                    <div style="color: #495057; font-size: 0.9rem;">
                        💰 ₹{driver.earnings_per_hour * 83:.0f}/hr
                    </div>
                    <div style="color: #495057; font-size: 0.9rem;">
                        😰 Stress: {driver.stress_score_mean:.1f}
                    </div>
                    <div style="color: #495057; font-size: 0.9rem;">
                        ⭐ {driver.safety_rating_mode}
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Full leaderboard table
    st.markdown('### 📊 Complete Leaderboard')
    
    # Prepare display data
    display_metrics = filtered_metrics[[
        'driver_id', 'overall_score', 'earnings_per_hour', 
        'stress_score_mean', 'safety_rating_mode'
    ]].copy()
    
    display_metrics.columns = [
        'Driver ID', 'Overall Score', 'Earnings (₹/hour)', 
        'Stress Score', 'Safety Rating'
    ]
    
    # Format earnings
    display_metrics['Earnings (₹/hour)'] = display_metrics['Earnings (₹/hour)'].apply(
        lambda x: f"₹{x * 83:.2f}"
    )
    
    # Add rank
    display_metrics.insert(0, 'Rank', range(1, len(display_metrics) + 1))
    
    # Style the top ranks
    def highlight_top_ranks(val):
        if isinstance(val, int) and val <= 3:
            return 'background-color: #ffd70033; font-weight: bold;'
        return ''
    
    styled_df = display_metrics.style.applymap(highlight_top_ranks, subset=['Rank'])
    
    st.dataframe(styled_df, width='stretch')
    
    # Performance distribution charts
    st.markdown('### 📈 Performance Distribution')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        fig_scores = px.histogram(
            filtered_metrics,
            x='overall_score',
            nbins=10,
            title='Overall Score Distribution',
            labels={'overall_score': 'Overall Score', 'count': 'Number of Drivers'},
            color_discrete_sequence=['#ffc107']
        )
        fig_scores.update_layout(height=400)
        st.plotly_chart(fig_scores, width='stretch')
    
    with col2:
        # Earnings vs Score scatter
        fig_scatter = px.scatter(
            filtered_metrics,
            x='overall_score',
            y='earnings_per_hour',
            color='safety_rating_mode',
            size='stress_score_mean',
            hover_name='driver_id',
            title='Score vs Earnings Analysis',
            labels={
                'overall_score': 'Overall Score',
                'earnings_per_hour': 'Earnings (₹/hour)',
                'safety_rating_mode': 'Safety Rating',
                'stress_score_mean': 'Stress Score'
            },
            height=400
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, width='stretch')
    
    # Safety rating breakdown
    st.markdown('### ⭐ Safety Rating Breakdown')
    
    safety_counts = filtered_metrics['safety_rating_mode'].value_counts()
    safety_avg_scores = filtered_metrics.groupby('safety_rating_mode')['overall_score'].mean()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = go.Figure(data=[
            go.Pie(
                labels=safety_counts.index,
                values=safety_counts.values,
                hole=0.3,
                marker_colors=['#28a745', '#17a2b8', '#ffc107', '#dc3545']
            )
        ])
        fig_pie.update_layout(
            title='Drivers by Safety Rating',
            height=400
        )
        st.plotly_chart(fig_pie, width='stretch')
    
    with col2:
        fig_bar = go.Figure(data=[
            go.Bar(
                x=safety_avg_scores.index,
                y=safety_avg_scores.values,
                marker_color=['#28a745', '#17a2b8', '#ffc107', '#dc3545']
            )
        ])
        fig_bar.update_layout(
            title='Average Score by Safety Rating',
            xaxis_title='Safety Rating',
            yaxis_title='Average Overall Score',
            height=400
        )
        st.plotly_chart(fig_bar, width='stretch')
    
    # Achievement badges
    st.markdown('### 🏅 Achievement Highlights')
    
    # Calculate achievements
    achievements = []
    
    # Highest earner
    highest_earner = filtered_metrics.loc[filtered_metrics['earnings_per_hour'].idxmax()]
    achievements.append({
        'badge': '💰',
        'title': 'Top Earner',
        'driver': f"Driver {highest_earner['driver_id']}",
        'value': f"₹{highest_earner['earnings_per_hour'] * 83:.0f}/hour"
    })
    
    # Safest driver
    filtered_metrics['safety_score'] = 10 - filtered_metrics['stress_score_mean']
    safest_driver = filtered_metrics.loc[filtered_metrics['safety_score'].idxmax()]
    achievements.append({
        'badge': '🛡️',
        'title': 'Safest Driver',
        'driver': f"Driver {safest_driver['driver_id']}",
        'value': f"Score: {safest_driver['safety_score']:.1f}/10"
    })
    
    # Most consistent (lowest stress variation)
    most_consistent = filtered_metrics.loc[filtered_metrics['stress_score_mean'].idxmin()]
    achievements.append({
        'badge': '😌',
        'title': 'Most Consistent',
        'driver': f"Driver {most_consistent['driver_id']}",
        'value': f"Stress: {most_consistent['stress_score_mean']:.1f}"
    })
    
    # Display achievements
    cols = st.columns(len(achievements))
    for i, (col, achievement) in enumerate(zip(cols, achievements)):
        with col:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                color: white;
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            ">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{achievement['badge']}</div>
                <div style="font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem;">
                    {achievement['title']}
                </div>
                <div style="font-size: 1rem; margin-bottom: 0.5rem;">
                    {achievement['driver']}
                </div>
                <div style="font-size: 0.9rem; opacity: 0.9;">
                    {achievement['value']}
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Export functionality
    st.markdown('### 📤 Export Leaderboard')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button('📊 Download as CSV', type='primary'):
            csv_data = display_metrics.to_csv(index=False)
            st.download_button(
                label='Download CSV',
                data=csv_data,
                file_name=f'driver_leaderboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                mime='text/csv'
            )
    
    with col2:
        if st.button('🔄 Refresh Data', type='secondary'):
            st.rerun()

if __name__ == "__main__":
    main()
