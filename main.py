"""
Driver Pulse Main Processing Pipeline
Orchestrates the complete data processing workflow.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_ingestion.load_data import DataLoader
from data_ingestion.clean_data import DataCleaner
from signal_processing.accelerometer_analysis import AccelerometerAnalyzer
from signal_processing.audio_analysis import AudioAnalyzer
from signal_processing.event_fusion import EventFusion
from earnings_forecast.velocity_model import EarningsVelocityModel
from earnings_forecast.goal_prediction import GoalPredictor
from processing.event_logger import EventLogger
from processing.trip_summary import TripSummarizer
from utils.config import config
from utils.helpers import load_sample_data_config


class DriverPulsePipeline:
    """Main pipeline orchestrator for Driver Pulse system."""
    
    def __init__(self, data_dir: str = "./data", output_dir: str = "./outputs"):
        self.data_dir = data_dir
        self.output_dir = output_dir
        
        # Initialize components
        self.data_loader = DataLoader(data_dir)
        self.data_cleaner = DataCleaner()
        self.accel_analyzer = AccelerometerAnalyzer()
        self.audio_analyzer = AudioAnalyzer()
        self.event_fusion = EventFusion()
        self.velocity_model = EarningsVelocityModel()
        self.goal_predictor = GoalPredictor()
        self.event_logger = EventLogger(output_dir)
        self.trip_summarizer = TripSummarizer()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def run_pipeline(self, generate_sample_data: bool = False):
        """Run the complete Driver Pulse pipeline."""
        print("🚗 Starting Driver Pulse Pipeline...")
        print("=" * 50)
        
        # Step 1: Generate sample data if requested
        if generate_sample_data:
            print("📊 Generating sample data...")
            self._generate_sample_data()
            print("✅ Sample data generated successfully")
        
        # Step 2: Load and clean data
        print("\n📂 Loading and cleaning data...")
        raw_data = self.data_loader.load_all_data()
        self.data_loader.validate_data_structure(raw_data)
        cleaned_data = self.data_cleaner.clean_all_data(raw_data)
        normalized_data = self.data_cleaner.normalize_signals(cleaned_data)
        print("✅ Data loaded and cleaned successfully")
        
        # Step 3: Signal processing
        print("\n🔍 Processing signals...")
        
        # Accelerometer analysis
        accel_df, accel_events = self.accel_analyzer.analyze_accelerometer_data(
            normalized_data['accelerometer']
        )
        
        # Audio analysis
        audio_df, audio_events = self.audio_analyzer.analyze_audio_data(
            normalized_data['audio']
        )
        
        print("✅ Signal processing completed")
        
        # Step 4: Event fusion
        print("\n🔗 Fusing multi-signal events...")
        fused_events = self.event_fusion.fuse_signals(accel_events, audio_events)
        fused_df = self.event_fusion.create_event_dataframe(fused_events)
        print("✅ Event fusion completed")
        
        # Step 5: Earnings analysis
        print("\n💰 Analyzing earnings and goals...")
        
        # Calculate earnings velocity
        velocity_data = self.velocity_model.calculate_earnings_velocity(
            normalized_data['earnings_log'],
            normalized_data['trips']
        )
        
        # Build velocity models
        self.velocity_model.build_velocity_models(velocity_data)
        
        # Generate forecasts
        forecasts = self.velocity_model.forecast_earnings(velocity_data)
        
        # Calculate velocity metrics
        velocity_metrics = self.velocity_model.calculate_velocity_metrics(velocity_data)
        
        # Predict goal achievement
        goal_predictions = self.goal_predictor.predict_goal_achievement(
            normalized_data['goals'],
            velocity_metrics,
            forecasts
        )
        
        print("✅ Earnings analysis completed")
        
        # Step 6: Generate outputs
        print("\n📋 Generating outputs...")
        
        # Create event logs
        flagged_logs = self.event_logger.create_flagged_moments_log(
            accel_events, audio_events, fused_events,
            accel_df, audio_df
        )
        
        # Create trip summaries
        trip_summaries = self.trip_summarizer.create_trip_summaries(
            normalized_data['trips'],
            fused_events,
            accel_events,
            audio_events
        )
        
        # Save trip summaries
        self.trip_summarizer.save_trip_summaries(trip_summaries)
        
        print("✅ Outputs generated successfully")
        
        # Step 7: Generate summary report
        print("\n📊 Generating summary report...")
        self._generate_summary_report(
            flagged_logs, trip_summaries, goal_predictions, velocity_metrics
        )
        
        print("\n🎉 Driver Pulse Pipeline completed successfully!")
        print(f"📁 Outputs saved to: {self.output_dir}")
        
        return {
            'flagged_events': flagged_logs,
            'trip_summaries': trip_summaries,
            'goal_predictions': goal_predictions,
            'velocity_metrics': velocity_metrics
        }
    
    def _generate_sample_data(self):
        """Generate comprehensive sample data for testing."""
        config_data = load_sample_data_config()
        
        # Generate drivers
        drivers = self._generate_drivers(config_data['drivers'])
        os.makedirs(f"{self.data_dir}/drivers", exist_ok=True)
        drivers.to_csv(f"{self.data_dir}/drivers/drivers.csv", index=False)
        
        # Generate trips
        trips = self._generate_trips(config_data['trips'], drivers['driver_id'].tolist())
        os.makedirs(f"{self.data_dir}/trips", exist_ok=True)
        trips.to_csv(f"{self.data_dir}/trips/trips.csv", index=False)
        
        # Generate sensor data
        accel_data = self._generate_accelerometer_data(config_data['accelerometer'], trips)
        audio_data = self._generate_audio_data(config_data['audio'], trips)
        os.makedirs(f"{self.data_dir}/sensor_data", exist_ok=True)
        accel_data.to_csv(f"{self.data_dir}/sensor_data/accelerometer_data.csv", index=False)
        audio_data.to_csv(f"{self.data_dir}/sensor_data/audio_intensity_data.csv", index=False)
        
        # Generate goals and earnings
        goals = self._generate_goals(config_data['goals'], drivers['driver_id'].tolist())
        earnings = self._generate_earnings_log(config_data['earnings'], trips, goals)
        os.makedirs(f"{self.data_dir}/earnings", exist_ok=True)
        goals.to_csv(f"{self.data_dir}/earnings/driver_goals.csv", index=False)
        earnings.to_csv(f"{self.data_dir}/earnings/earnings_velocity_log.csv", index=False)
    
    def _generate_drivers(self, config: dict) -> pd.DataFrame:
        """Generate sample driver data."""
        np.random.seed(42)
        
        drivers = []
        for i in range(config['count']):
            driver_id = f"driver_{i+1:03d}"
            rating = np.random.uniform(*config['rating_range'])
            city = np.random.choice(config['cities'])
            
            drivers.append({
                'driver_id': driver_id,
                'rating': round(rating, 2),
                'city': city
            })
        
        return pd.DataFrame(drivers)
    
    def _generate_trips(self, config: dict, driver_ids: list) -> pd.DataFrame:
        """Generate sample trip data."""
        np.random.seed(42)
        trips = []
        
        base_time = datetime.now() - timedelta(days=config['date_range'])
        
        for driver_id in driver_ids:
            for trip_num in range(config['count_per_driver']):
                # Generate trip times
                start_offset = np.random.randint(0, config['date_range'] * 24 * 60)
                start_time = base_time + timedelta(minutes=start_offset)
                
                duration = np.random.randint(*config['duration_range'])
                end_time = start_time + timedelta(minutes=duration)
                
                fare = np.random.uniform(*config['fare_range'])
                
                trips.append({
                    'trip_id': f"{driver_id}_trip_{trip_num+1:03d}",
                    'driver_id': driver_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'fare': round(fare, 2)
                })
        
        return pd.DataFrame(trips)
    
    def _generate_accelerometer_data(self, config: dict, trips: pd.DataFrame) -> pd.DataFrame:
        """Generate sample accelerometer data."""
        np.random.seed(42)
        accel_data = []
        
        for _, trip in trips.iterrows():
            duration_minutes = (trip['end_time'] - trip['start_time']).total_seconds() / 60
            num_samples = min(int(duration_minutes * config['sampling_rate']), config['samples_per_trip'])
            
            for i in range(num_samples):
                timestamp = trip['start_time'] + timedelta(seconds=i * 60 / config['sampling_rate'])
                
                # Generate realistic accelerometer data
                ax = np.random.normal(0, 0.5)  # Normal driving
                ay = np.random.normal(0, 0.3)
                az = 9.81 + np.random.normal(0, 0.2)  # Gravity + noise
                
                # Occasionally add harsh events
                if np.random.random() < 0.05:  # 5% chance of harsh event
                    if np.random.random() < 0.5:
                        ax = np.random.uniform(-3, -2.5)  # Harsh braking
                    else:
                        ax = np.random.uniform(2.5, 3)    # Harsh acceleration
                
                accel_data.append({
                    'timestamp': timestamp,
                    'ax': round(ax, 3),
                    'ay': round(ay, 3),
                    'az': round(az, 3)
                })
        
        return pd.DataFrame(accel_data)
    
    def _generate_audio_data(self, config: dict, trips: pd.DataFrame) -> pd.DataFrame:
        """Generate sample audio intensity data."""
        np.random.seed(42)
        audio_data = []
        
        for _, trip in trips.iterrows():
            duration_minutes = (trip['end_time'] - trip['start_time']).total_seconds() / 60
            num_samples = min(int(duration_minutes * config['sampling_rate']), config['samples_per_trip'])
            
            for i in range(num_samples):
                timestamp = trip['start_time'] + timedelta(seconds=i * 60 / config['sampling_rate'])
                
                # Generate realistic audio data
                db_level = config['baseline_db'] + np.random.normal(0, 5)
                
                # Occasionally add noise events
                if np.random.random() < 0.08:  # 8% chance of noise event
                    db_level = np.random.uniform(*config['noise_range'])
                
                audio_data.append({
                    'timestamp': timestamp,
                    'decibel_level': round(db_level, 1)
                })
        
        return pd.DataFrame(audio_data)
    
    def _generate_goals(self, config: dict, driver_ids: list) -> pd.DataFrame:
        """Generate sample driver goals."""
        np.random.seed(42)
        goals = []
        
        for driver_id in driver_ids:
            daily_goal = np.random.uniform(*config['daily_goal_range'])
            
            goals.append({
                'driver_id': driver_id,
                'daily_goal': round(daily_goal, 2)
            })
        
        return pd.DataFrame(goals)
    
    def _generate_earnings_log(self, config: dict, trips: pd.DataFrame, goals: pd.DataFrame) -> pd.DataFrame:
        """Generate sample earnings velocity log."""
        np.random.seed(42)
        earnings_log = []
        
        # Create goals lookup
        goal_lookup = goals.set_index('driver_id')['daily_goal'].to_dict()
        
        # Group trips by driver
        for driver_id in trips['driver_id'].unique():
            driver_trips = trips[trips['driver_id'] == driver_id].sort_values('start_time')
            daily_goal = goal_lookup.get(driver_id, 200)
            
            cumulative_earnings = 0
            
            for _, trip in driver_trips.iterrows():
                cumulative_earnings += trip['fare']
                
                # Add some variance to earnings
                variance = np.random.normal(0, config['earning_variance'] * trip['fare'])
                reported_earnings = cumulative_earnings + variance
                
                earnings_log.append({
                    'timestamp': trip['end_time'],
                    'driver_id': driver_id,
                    'earnings': round(max(0, reported_earnings), 2)
                })
        
        return pd.DataFrame(earnings_log)
    
    def _generate_summary_report(self, flagged_logs, trip_summaries, goal_predictions, velocity_metrics):
        """Generate a comprehensive summary report."""
        report_path = os.path.join(self.output_dir, "pipeline_summary.txt")
        
        with open(report_path, 'w') as f:
            f.write("DRIVER PULSE PIPELINE SUMMARY REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {datetime.now()}\n\n")
            
            # Event summary
            f.write("EVENT DETECTION SUMMARY\n")
            f.write("-" * 25 + "\n")
            if not flagged_logs.empty:
                f.write(f"Total events detected: {len(flagged_logs)}\n")
                f.write(f"Events by type: {flagged_logs['event_label'].value_counts().to_dict()}\n")
                f.write(f"Events by severity: {flagged_logs['severity'].value_counts().to_dict()}\n")
                f.write(f"Average confidence: {flagged_logs['confidence'].mean():.2f}\n")
            else:
                f.write("No events detected.\n")
            f.write("\n")
            
            # Trip summary
            f.write("TRIP ANALYSIS SUMMARY\n")
            f.write("-" * 23 + "\n")
            if not trip_summaries.empty:
                f.write(f"Total trips: {len(trip_summaries)}\n")
                f.write(f"Total earnings: ${trip_summaries['fare'].sum():.2f}\n")
                f.write(f"Average trip duration: {trip_summaries['duration_minutes'].mean():.1f} minutes\n")
                f.write(f"Average stress score: {trip_summaries['stress_score'].mean():.2f}\n")
                f.write(f"Safety rating distribution: {trip_summaries['safety_rating'].value_counts().to_dict()}\n")
            else:
                f.write("No trip data available.\n")
            f.write("\n")
            
            # Goal prediction summary
            f.write("GOAL PREDICTION SUMMARY\n")
            f.write("-" * 25 + "\n")
            if not goal_predictions.empty:
                f.write(f"Drivers with goals: {len(goal_predictions)}\n")
                f.write(f"Goal status distribution: {goal_predictions['goal_status'].value_counts().to_dict()}\n")
                f.write(f"Average goal progress: {goal_predictions['progress_percentage'].mean():.1f}%\n")
                f.write(f"Average achievement probability: {goal_predictions['achievement_probability'].mean():.2f}\n")
            else:
                f.write("No goal predictions available.\n")
            f.write("\n")
            
            # Velocity metrics summary
            f.write("EARNINGS VELOCITY SUMMARY\n")
            f.write("-" * 28 + "\n")
            if not velocity_metrics.empty:
                f.write(f"Drivers analyzed: {len(velocity_metrics)}\n")
                f.write(f"Average earnings/hour: ${velocity_metrics['avg_earnings_per_hour'].mean():.2f}\n")
                f.write(f"Average velocity consistency: {velocity_metrics['velocity_consistency'].mean():.2f}\n")
                f.write(f"Total hours worked: {velocity_metrics['total_hours_worked'].sum():.1f}\n")
            else:
                f.write("No velocity metrics available.\n")
        
        print(f"📄 Summary report saved to: {report_path}")


def main():
    """Main entry point for the Driver Pulse pipeline."""
    parser = argparse.ArgumentParser(description='Driver Pulse Data Processing Pipeline')
    parser.add_argument('--generate-sample-data', action='store_true',
                       help='Generate sample data for testing')
    parser.add_argument('--data-dir', default='./data',
                       help='Data directory path')
    parser.add_argument('--output-dir', default='./outputs',
                       help='Output directory path')
    
    args = parser.parse_args()
    
    # Validate configuration
    if not config.validate_paths():
        print("❌ Error: Could not create required directories")
        return 1
    
    # Run pipeline
    pipeline = DriverPulsePipeline(args.data_dir, args.output_dir)
    
    try:
        results = pipeline.run_pipeline(generate_sample_data=args.generate_sample_data)
        print("\n🎯 Pipeline completed successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
