"""
Driver Comparison Page - Side-by-side comparison of multiple drivers
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
    """Driver comparison page with side-by-side analysis."""
    
    # Page header
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 15px 40px rgba(23, 162, 184, 0.3);
    ">
        <h1 style="
            color: white; 
            margin: 0; 
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        ">
            👥 Driver Comparison
        </h1>
        <p style="
            color: rgba(255,255,255,0.95);
            margin: 1rem 0 0 0;
            font-size: 1.2rem;
            font-weight: 400;
        ">
            Side-by-side analysis and comparison of driver performance metrics
        </p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = DriverPulseDashboard()
    
    if 'driver_metrics' not in dashboard.data:
        st.error('No driver data available for comparison.')
        return
    
    metrics = dashboard.data['driver_metrics'].copy()
    
    # Driver selection interface
    st.markdown('### 🎯 Select Drivers to Compare')
    
    # Get available drivers
    available_drivers = sorted(metrics['driver_id'].unique().tolist())
    
    # Multi-select for driver comparison
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_drivers = st.multiselect(
            'Choose drivers to compare:',
            available_drivers,
            default=available_drivers[:2] if len(available_drivers) >= 2 else available_drivers,
            max_selections=5,
            help='Select up to 5 drivers for detailed comparison'
        )
    
    
    
    if len(selected_drivers) < 2:
        st.warning('Please select at least 2 drivers to compare.')
        return
    
    # Filter selected drivers
    comparison_data = metrics[metrics['driver_id'].isin(selected_drivers)].copy()
    
    # Comparison overview cards
    st.markdown('### 📊 Comparison Overview')
    
    # Create comparison cards
    cols = st.columns(len(selected_drivers))
    
    colors = ['#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1']
    
    for i, (col, driver_id, color) in enumerate(zip(cols, selected_drivers, colors)):
        driver_data = comparison_data[comparison_data['driver_id'] == driver_id].iloc[0]
        
        with col:
            st.markdown(f'''
            <div style="
                background: linear-gradient(135deg, {color}22 0%, {color}11 100%);
                padding: 1.5rem;
                border-radius: 15px;
                text-align: center;
                border: 2px solid {color};
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            ">
                <h3 style="color: {color}; margin: 0 0 1rem 0; font-size: 1.3rem;">
                    Driver {driver_id}
                </h3>
                <div style="font-size: 1.8rem; font-weight: bold; color: #495057; margin: 0.5rem 0;">
                    {driver_data['overall_score']:.1f}
                </div>
                <div style="color: #6c757d; font-size: 0.9rem;">Overall Score</div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #dee2e6;">
                    <div style="color: #495057; font-size: 0.9rem; margin: 0.25rem 0;">
                        💰 ₹{driver_data['earnings_per_hour'] * 83:.0f}/hr
                    </div>
                    <div style="color: #495057; font-size: 0.9rem; margin: 0.25rem 0;">
                        😰 Stress: {driver_data['stress_score_mean']:.1f}
                    </div>
                    <div style="color: #495057; font-size: 0.9rem; margin: 0.25rem 0;">
                        ⭐ {driver_data['safety_rating_mode']}
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Detailed comparison table
    st.markdown('### 📋 Detailed Metrics Comparison')
    
    # Prepare comparison table
    comparison_metrics = {}
    
    for driver_id in selected_drivers:
        driver_data = comparison_data[comparison_data['driver_id'] == driver_id].iloc[0]
        comparison_metrics[f'Driver {driver_id}'] = [
            f"{driver_data['overall_score']:.2f}",
            f"₹{driver_data['earnings_per_hour'] * 83:.2f}",
            f"{driver_data['stress_score_mean']:.2f}",
            driver_data['safety_rating_mode']
        ]
    
    comparison_df = pd.DataFrame(
        comparison_metrics,
        index=['Overall Score', 'Earnings/Hour', 'Stress Score', 'Safety Rating']
    )
    
    # Highlight best values
    def highlight_best(val, col_name, row_name):
        if row_name == 'Overall Score':
            best = comparison_df.loc['Overall Score'].astype(float).max()
            if float(val) == best:
                return 'background-color: #d4edda; font-weight: bold;'
        elif row_name == 'Earnings/Hour':
            earnings_vals = comparison_df.loc['Earnings/Hour'].str.replace('₹', '').str.replace('/hr', '').astype(float)
            best = earnings_vals.max()
            if float(val.replace('₹', '').replace('/hr', '')) == best:
                return 'background-color: #d4edda; font-weight: bold;'
        elif row_name == 'Stress Score':
            best = comparison_df.loc['Stress Score'].astype(float).min()
            if float(val) == best:
                return 'background-color: #d4edda; font-weight: bold;'
        return ''
    
    styled_df = comparison_df.style.apply(
        lambda x: [highlight_best(x[i], x.name, comparison_df.index[i]) for i in range(len(x))],
        axis=0
    )
    
    st.dataframe(styled_df, width='stretch')
    
    # Visual comparisons
    st.markdown('### 📈 Visual Performance Comparison')
    
    # Radar chart for multi-dimensional comparison
    fig_radar = go.Figure()
    
    # Prepare radar data
    categories = ['Overall Score', 'Earnings/Hour', 'Safety', 'Low Stress']
    
    for i, driver_id in enumerate(selected_drivers):
        driver_data = comparison_data[comparison_data['driver_id'] == driver_id].iloc[0]
        
        # Normalize values for radar chart
        overall_norm = (driver_data['overall_score'] / 100) * 100
        earnings_norm = (driver_data['earnings_per_hour'] / comparison_data['earnings_per_hour'].max()) * 100
        safety_score = 10 - driver_data['stress_score_mean']
        safety_norm = (safety_score / 10) * 100
        stress_norm = ((10 - driver_data['stress_score_mean']) / 10) * 100
        
        values = [overall_norm, earnings_norm, safety_norm, stress_norm]
        values.append(values[0])  # Close the radar chart
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=f'Driver {driver_id}',
            line_color=colors[i % len(colors)]
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Multi-Dimensional Performance Comparison",
        height=500
    )
    
    st.plotly_chart(fig_radar, width='stretch')
    
    # Bar charts for individual metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Overall score comparison
        fig_score = go.Figure(data=[
            go.Bar(
                x=[f'Driver {d}' for d in selected_drivers],
                y=[comparison_data[comparison_data['driver_id'] == d]['overall_score'].iloc[0] for d in selected_drivers],
                marker_color=colors[:len(selected_drivers)]
            )
        ])
        fig_score.update_layout(
            title='Overall Score Comparison',
            xaxis_title='Driver',
            yaxis_title='Score',
            height=400
        )
        st.plotly_chart(fig_score, width='stretch')
    
    with col2:
        # Earnings comparison
        fig_earnings = go.Figure(data=[
            go.Bar(
                x=[f'Driver {d}' for d in selected_drivers],
                y=[comparison_data[comparison_data['driver_id'] == d]['earnings_per_hour'].iloc[0] for d in selected_drivers],
                marker_color=colors[:len(selected_drivers)]
            )
        ])
        fig_earnings.update_layout(
            title='Earnings per Hour Comparison',
            xaxis_title='Driver',
            yaxis_title='Earnings (₹/hour)',
            height=400
        )
        st.plotly_chart(fig_earnings, width='stretch')
    
    # Performance trends (if trip data available)
    if 'trips' in dashboard.data:
        st.markdown('### 📊 Performance Trends')
        
        trips = dashboard.data['trips'].copy()
        trips['date'] = pd.to_datetime(trips['start_time']).dt.date
        
        # Filter trips for selected drivers
        selected_trips = trips[trips['driver_id'].isin(selected_drivers)]
        
        if not selected_trips.empty:
            # Daily earnings trend
            daily_earnings = selected_trips.groupby(['driver_id', 'date'])['fare'].sum().reset_index()
            
            fig_trend = px.line(
                daily_earnings,
                x='date',
                y='fare',
                color='driver_id',
                title='Daily Earnings Trend Comparison',
                labels={'fare': 'Total Earnings ($)', 'date': 'Date', 'driver_id': 'Driver'},
                color_discrete_map={f'{d}': colors[i] for i, d in enumerate(selected_drivers)},
                height=400
            )
            
            fig_trend.update_traces(line_width=3)
            st.plotly_chart(fig_trend, width='stretch')
    
    # Head-to-head analysis
    if len(selected_drivers) == 2:
        st.markdown('### ⚔️ Head-to-Head Analysis')
    
        driver1, driver2 = selected_drivers
    
        d1_data = comparison_data[comparison_data['driver_id'] == driver1].iloc[0]
        d2_data = comparison_data[comparison_data['driver_id'] == driver2].iloc[0]
    
        # Safe metric extraction (prevents empty boxes)
        metrics_comparison = {
            "Overall Score": (
                float(d1_data.get("overall_score", 0)),
                float(d2_data.get("overall_score", 0))
            ),
            "Earnings/Hour": (
                float(d1_data.get("earnings_per_hour", 0)),
                float(d2_data.get("earnings_per_hour", 0))
            ),
            "Stress Score": (
                float(d1_data.get("stress_score_mean", 0)),
                float(d2_data.get("stress_score_mean", 0))
            ),
            "Safety Score": (
                10 - float(d1_data.get("stress_score_mean", 0)),
                10 - float(d2_data.get("stress_score_mean", 0))
            )
        }
    
        col1, col2 = st.columns(2)

        # DRIVER 1
        with col1:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #28a745, #20c997);
                padding:1.5rem;
                border-radius:15px;
                color:white;
                text-align:center;">
                <h3>🚗 Driver {driver1}</h3>
            </div>
            """, unsafe_allow_html=True)

            for metric, (v1, v2) in metrics_comparison.items():

                if metric == "Earnings/Hour":
                    value = f"₹{v1*83:.2f}"
                else:
                    value = f"{v1:.2f}"

                st.markdown(
                    f"""
                    <div style="
                        background:#1e1e1e;
                        color:white;
                        padding:1rem;
                        border-radius:10px;
                        margin-bottom:0.5rem;
                        border-left:4px solid #28a745;">
                        <strong>{metric}:</strong> {value}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # DRIVER 2
        with col2:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #17a2b8, #138496);
                padding:1.5rem;
                border-radius:15px;
                color:white;
                text-align:center;">
                <h3>🚙 Driver {driver2}</h3>
            </div>
            """, unsafe_allow_html=True)

            for metric, (v1, v2) in metrics_comparison.items():

                if metric == "Earnings/Hour":
                    value = f"₹{v2*83:.2f}"
                else:
                    value = f"{v2:.2f}"

                st.markdown(
                    f"""
                    <div style="
                        background:#1e1e1e;
                        color:white;
                        padding:1rem;
                        border-radius:10px;
                        margin-bottom:0.5rem;
                        border-left:4px solid #17a2b8;">
                        <strong>{metric}:</strong> {value}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    
        # Winner analysis
        st.markdown("### 🏆 Winner Analysis")
    
        wins = {"Driver 1": 0, "Driver 2": 0, "Tie": 0}
    
        for metric, (v1, v2) in metrics_comparison.items():
    
            if metric == "Stress Score":
                if v1 < v2:
                    wins["Driver 1"] += 1
                elif v2 < v1:
                    wins["Driver 2"] += 1
                else:
                    wins["Tie"] += 1
            else:
                if v1 > v2:
                    wins["Driver 1"] += 1
                elif v2 > v1:
                    wins["Driver 2"] += 1
                else:
                    wins["Tie"] += 1
    
        winner = max(wins, key=wins.get)
    
        if winner == "Driver 1":
            winner_text = f"🏆 Driver {driver1} wins!"
            winner_color = "#28a745"
        elif winner == "Driver 2":
            winner_text = f"🏆 Driver {driver2} wins!"
            winner_color = "#17a2b8"
        else:
            winner_text = "🤝 It's a tie!"
            winner_color = "#ffc107"
    
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {winner_color}22, {winner_color}11);
            padding:2rem;
            border-radius:15px;
            text-align:center;
            border:2px solid {winner_color};">
            <h2 style="color:{winner_color};">{winner_text}</h2>
            <p>
            Driver {driver1}: {wins['Driver 1']} wins |
            Driver {driver2}: {wins['Driver 2']} wins |
            Ties: {wins['Tie']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Export comparison
    st.markdown('### 📤 Export Comparison')
    
    if st.button('📊 Download Comparison Report', type='primary'):
        # Create comparison report
        report_data = {
            'Comparison Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Drivers Compared': ', '.join([f'Driver {d}' for d in selected_drivers]),
            'Metrics': ['Overall Score', 'Earnings/Hour', 'Stress Score', 'Safety Rating']
        }
        
        # Add detailed metrics
        for driver_id in selected_drivers:
            driver_data = comparison_data[comparison_data['driver_id'] == driver_id].iloc[0]
            report_data[f'Driver {driver_id} - Overall Score'] = f"{driver_data['overall_score']:.2f}"
            report_data[f'Driver {driver_id} - Earnings/Hour'] = f"₹{driver_data['earnings_per_hour'] * 83:.2f}"
            report_data[f'Driver {driver_id} - Stress Score'] = f"{driver_data['stress_score_mean']:.2f}"
            report_data[f'Driver {driver_id} - Safety Rating'] = driver_data['safety_rating_mode']
        
        # Convert to DataFrame and download
        report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
        csv_data = report_df.to_csv(index=False)
        
        st.download_button(
            label='Download Comparison Report',
            data=csv_data,
            file_name=f'driver_comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()
