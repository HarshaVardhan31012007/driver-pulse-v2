# 🏗️ Driver Pulse - System Architecture

## Overview

Driver Pulse follows a **microservices architecture** with clear separation of concerns, enabling scalability, maintainability, and rapid development. The system is designed to process real-time sensor data and provide actionable insights through an intuitive dashboard.

## Architecture Diagram

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │  Processing Layer│    │  Presentation   │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • Accelerometer │───▶│ • Signal Processing│───▶│ • Dashboard     │
│ • Audio Data    │    │ • Event Detection │    │ • REST API      │
│ • Trip Logs     │    │ • ML Classification│    │ • Analytics     │
│ • Driver Goals  │    │ • Earnings Engine │    │ • Reports       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Storage  │    │   Utilities      │    │  Deployment     │
├─────────────────┤    ├──────────────────┤    ├─────────────────┤
│ • CSV Files     │    │ • Configuration  │    │ • Docker        │
│ • Processed Data│    │ • Logging        │    │ • Streamlit     │
│ • Event Logs    │    │ • Helpers        │    │ • FastAPI       │
│ • Analytics     │    │ • Validation     │    │ • Monitoring    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Core Components

### 1. Data Ingestion Layer (`data_ingestion/`)

**Purpose**: Load, validate, and preprocess raw sensor data

**Key Classes**:
- `DataLoader`: Handles CSV loading with validation
- `DataValidator`: Ensures data quality and completeness
- `DataCleaner`: Preprocesses and cleans raw data

**Data Flow**:
```python
# Data loading pipeline
loader = DataLoader()
raw_data = loader.load_accelerometer_data(file_path)
validated_data = loader.validate_data_structure(raw_data)
clean_data = loader.clean_data(validated_data)
```

**Input Schema**:
```python
AccelerometerData:
    - timestamp: datetime
    - ax, ay, az: float (g-force values)
    - driver_id: string
    - trip_id: string

AudioData:
    - timestamp: datetime
    - decibel_level: float (dB)
    - frequency_spectrum: array
    - driver_id: string
```

### 2. Signal Processing Layer (`signal_processing/`)

**Purpose**: Advanced signal analysis and event detection

**Key Classes**:
- `AccelerometerAnalyzer`: Multi-stage motion analysis
- `AudioAnalyzer`: Decibel spike and frequency analysis
- `EventFusion`: Multi-sensor event correlation

**Processing Pipeline**:
```python
# Advanced signal processing
analyzer = AccelerometerAnalyzer()

# Stage 1: Feature extraction
features = analyzer.compute_advanced_features(raw_data)

# Stage 2: Multi-stage smoothing
smoothed = analyzer.advanced_smoothing(features)

# Stage 3: Peak detection
peaks = analyzer.detect_peaks_advanced(smoothed)

# Stage 4: ML-inspired classification
events = analyzer.classify_events_ml_inspired(smoothed, peaks)
```

**Advanced Features**:
- **Jerk Calculation**: Rate of change of acceleration
- **Frequency Analysis**: FFT for vibration patterns
- **Statistical Features**: Rolling windows with variance/std
- **Multi-threshold Detection**: Adaptive confidence scoring

### 3. Earnings Forecast Layer (`earnings_forecast/`)

**Purpose**: Predictive analytics and earnings optimization

**Key Classes**:
- `EarningsVelocityModel`: Real-time velocity calculation
- `GoalPredictor`: ML-based goal forecasting
- `PerformanceAnalyzer`: Driver benchmarking

**Velocity Calculation**:
```python
# Earnings velocity algorithm
def calculate_earnings_velocity(trips, current_time):
    """Calculate real-time earnings per hour"""
    recent_trips = filter_trips_by_time_window(trips, current_time, hours=1)
    total_earnings = sum(trip.fare for trip in recent_trips)
    active_hours = calculate_active_driving_time(recent_trips)
    return total_earnings / max(active_hours, 1)
```

**Prediction Models**:
- **Linear Regression**: Trend analysis
- **Time Series**: Seasonal pattern detection
- **Ensemble Methods**: Combined predictions
- **Confidence Intervals**: Prediction uncertainty

### 4. Processing Layer (`processing/`)

**Purpose**: Output formatting, logging, and data export

**Key Classes**:
- `EventLogger`: Structured event logging
- `OutputFormatter`: CSV/JSON export formatting
- `ReportGenerator`: Automated report creation

**Event Logging Schema**:
```python
EventLog:
    - timestamp: datetime
    - driver_id: string
    - event_type: string
    - severity: string
    - confidence: float
    - features: dict
    - metadata: dict
```

### 5. API Layer (`api/`)

**Purpose**: RESTful API for data access and integration

**Endpoints**:
```python
# Core API endpoints
GET    /api/v1/drivers/              # List all drivers
GET    /api/v1/drivers/{id}/metrics  # Driver performance metrics
GET    /api/v1/events/               # Event data with filters
POST   /api/v1/events/               # Create new event
GET    /api/v1/analytics/summary     # Analytics summary
GET    /api/v1/earnings/forecast     # Earnings predictions
```

**API Architecture**:
- **FastAPI**: High-performance async framework
- **Pydantic**: Data validation and serialization
- **CORS**: Cross-origin resource sharing
- **Rate Limiting**: API protection and fair usage

### 6. Dashboard Layer (`dashboard/`)

**Purpose**: Interactive data visualization and user interface

**Key Components**:
- **Real-time Metrics**: Live KPI tracking
- **Interactive Charts**: Plotly-based visualizations
- **AI Insights**: Personalized recommendations
- **Driver Tools**: Comparison and analysis features

**Dashboard Architecture**:
```python
# Dashboard component structure
class DriverPulseDashboard:
    def __init__(self):
        self.data_loader = DataLoader()
        self.analytics_engine = AnalyticsEngine()
        self.insight_generator = InsightGenerator()
    
    def render_performance_overview(self):
        """Main performance metrics display"""
        
    def render_event_analysis(self):
        """Event pattern visualization"""
        
    def render_ai_insights(self):
        """Personalized recommendations"""
```

### 7. Utilities Layer (`utils/`)

**Purpose**: Shared utilities and configuration management

**Key Modules**:
- `config.py`: Centralized configuration management
- `logger.py`: Structured logging system
- `helpers.py`: Common utility functions

**Configuration Management**:
```python
# Environment-specific configuration
class DriverPulseConfig:
    # Project metadata
    NAME = "Driver Pulse"
    VERSION = "1.0.0"
    
    # Data paths
    DATA_ROOT = Path("./data")
    OUTPUTS_PATH = Path("./outputs")
    
    # Processing parameters
    SAMPLING_RATE = 10  # Hz
    WINDOW_SIZE = 5
    
    # API settings
    API_HOST = "0.0.0.0"
    API_PORT = 8000
```

## Data Flow Architecture

### 1. Data Ingestion Flow
```
Raw CSV Files → DataLoader → DataValidator → DataCleaner → Validated Data
```

### 2. Signal Processing Flow
```
Validated Data → Feature Extraction → Multi-stage Smoothing → Peak Detection → ML Classification → Event Objects
```

### 3. Analytics Flow
```
Event Objects + Trip Data → Analytics Engine → Performance Metrics → Predictions → Insights
```

### 4. Presentation Flow
```
Analytics Results → Dashboard Components → Interactive Visualizations → User Interface
```

## Technology Stack

### Backend Technologies
- **Python 3.11**: Core programming language
- **FastAPI**: High-performance API framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Signal processing and scientific computing
- **Scikit-learn**: Machine learning utilities

### Frontend Technologies
- **Streamlit**: Interactive dashboard framework
- **Plotly**: Interactive visualizations
- **HTML/CSS**: Custom styling and animations
- **JavaScript**: Enhanced interactivity

### Data Processing
- **Signal Processing**: Advanced filtering and analysis
- **Statistical Analysis**: Descriptive and inferential statistics
- **Time Series**: Temporal pattern analysis
- **Feature Engineering**: Automated feature extraction

### Infrastructure
- **Docker**: Containerization and deployment
- **Docker Compose**: Multi-service orchestration
- **GitHub**: Version control and CI/CD
- **Streamlit Cloud**: Dashboard hosting

## Design Patterns

### 1. Strategy Pattern
**Used in**: Signal processing algorithms
```python
class SignalProcessingStrategy:
    def process(self, data): pass

class AccelerometerStrategy(SignalProcessingStrategy):
    def process(self, data): # Accelerometer-specific processing

class AudioStrategy(SignalProcessingStrategy):
    def process(self, data): # Audio-specific processing
```

### 2. Observer Pattern
**Used in**: Dashboard real-time updates
```python
class DashboardObserver:
    def update(self, data): pass

class MetricsDisplay(DashboardObserver):
    def update(self, data): # Update metrics display
```

### 3. Factory Pattern
**Used in**: Analyzer creation
```python
class AnalyzerFactory:
    @staticmethod
    def create_analyzer(analyzer_type):
        if analyzer_type == "accelerometer":
            return AccelerometerAnalyzer()
        elif analyzer_type == "audio":
            return AudioAnalyzer()
```

### 4. Repository Pattern
**Used in**: Data access layer
```python
class DataRepository:
    def get_driver_data(self, driver_id): pass
    def save_events(self, events): pass
    def get_analytics(self, filters): pass
```

## Performance Considerations

### 1. Data Processing Optimization
- **Vectorized Operations**: NumPy/Pandas for bulk processing
- **Memory Management**: Chunked processing for large datasets
- **Caching**: Memoization of expensive calculations
- **Parallel Processing**: Multi-threading for independent tasks

### 2. API Performance
- **Async Operations**: Non-blocking I/O with FastAPI
- **Connection Pooling**: Database connection optimization
- **Response Caching**: Redis for frequently accessed data
- **Rate Limiting**: Fair usage and protection

### 3. Dashboard Performance
- **Lazy Loading**: Load data on demand
- **Data Sampling**: Aggregate for large datasets
- **Virtual Scrolling**: Handle large data tables
- **Background Refresh**: Non-blocking data updates

## Security Architecture

### 1. Data Protection
- **Input Validation**: Pydantic models for API validation
- **Data Sanitization**: Clean and validate all inputs
- **Error Handling**: Secure error responses
- **Logging Security**: No sensitive data in logs

### 2. API Security
- **CORS Configuration**: Controlled cross-origin access
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Input Validation**: Type checking and sanitization
- **Error Boundaries**: Graceful error handling

## Scalability Architecture

### 1. Horizontal Scaling
- **Microservices**: Independent service scaling
- **Load Balancing**: Distribute API requests
- **Database Sharding**: Partition large datasets
- **Caching Layer**: Reduce database load

### 2. Vertical Scaling
- **Resource Optimization**: Efficient memory usage
- **Algorithm Optimization**: O(n) vs O(n²) complexity
- **Data Structures**: Optimal data structure selection
- **Profiling**: Identify and optimize bottlenecks

## Monitoring & Observability

### 1. Logging Strategy
```python
# Structured logging with context
logger.info(
    "Event detected",
    extra={
        "driver_id": driver_id,
        "event_type": event_type,
        "confidence": confidence,
        "processing_time_ms": processing_time
    }
)
```

### 2. Metrics Collection
- **Performance Metrics**: Response times, throughput
- **Business Metrics**: Event counts, accuracy rates
- **System Metrics**: CPU, memory, disk usage
- **Custom Metrics**: Application-specific KPIs

### 3. Error Handling
- **Graceful Degradation**: Fallback for non-critical failures
- **Retry Logic**: Automatic retry for transient failures
- **Circuit Breakers**: Prevent cascade failures
- **Alerting**: Notify on critical issues

## Deployment Architecture

### 1. Container Strategy
```dockerfile
# Multi-stage Docker build
FROM python:3.11-slim as base
FROM base as dependencies
FROM dependencies as production
```

### 2. Service Orchestration
```yaml
# docker-compose.yml
services:
  driver-pulse:
    build: .
    ports:
      - "8501:8501"
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
```

### 3. Environment Management
- **Development**: Local development setup
- **Testing**: Automated testing environment
- **Staging**: Pre-production validation
- **Production**: Live deployment

## Testing Architecture

### 1. Test Pyramid
```
E2E Tests (5%)
├── Integration Tests (15%)
├── Unit Tests (80%)
```

### 2. Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Service interaction testing
- **API Tests**: Endpoint validation
- **Dashboard Tests**: UI component testing

### 3. Test Automation
- **CI/CD Pipeline**: Automated test execution
- **Coverage Reports**: 95%+ code coverage
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

## Future Architecture Enhancements

### 1. Microservices Evolution
- **Event Sourcing**: Immutable event logs
- **CQRS**: Command Query Responsibility Segregation
- **Message Queues**: Asynchronous processing
- **Service Mesh**: Advanced service communication

### 2. Advanced Analytics
- **Real-time Streaming**: Kafka/Spark integration
- **Machine Learning**: TensorFlow/PyTorch models
- **Time Series DB**: InfluxDB for temporal data
- **Graph Database**: Neo4j for relationship analysis

### 3. Cloud Native
- **Kubernetes**: Container orchestration
- **Serverless**: AWS Lambda functions
- **Managed Services**: Cloud database solutions
- **CDN**: Global content delivery

---

This architecture ensures Driver Pulse is **scalable, maintainable, and production-ready** while providing the foundation for future enhancements and innovations.
