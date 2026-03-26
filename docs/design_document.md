# Driver Pulse Design Document

## Product Vision

Driver Pulse transforms raw sensor data from driver phones into actionable insights about safety moments and earnings velocity. Our vision is to empower Uber drivers with real-time awareness of their driving patterns and financial progress, enabling them to make informed decisions that improve both safety and earnings.

### Core Value Propositions

1. **Safety Awareness**: Identify potentially stressful or risky driving moments through multi-signal analysis
2. **Earnings Intelligence**: Provide clear visibility into earnings pace and goal achievement probability
3. **Actionable Insights**: Deliver personalized recommendations for improving driving performance
4. **Privacy-First**: Analyze aggregated signal patterns without storing sensitive audio or location data

## User Persona

### Primary User: "Alex the Uber Driver"

**Demographics:**
- Age: 32 years old
- Experience: 2 years driving for Uber
- Location: Major metropolitan area
- Goals: Maximize earnings while maintaining safety ratings
- Tech Comfort: High (uses smartphone apps daily)

**Pain Points:**
- Uncertainty about daily earnings progress
- Lack of feedback on driving safety incidents
- Difficulty optimizing routes and timing
- Stress from passenger conflicts or traffic situations

**Needs:**
- Real-time earnings tracking
- Clear safety metrics
- Actionable improvement suggestions
- Easy-to-understand interface

**Usage Context:**
- Checks dashboard between rides
- Reviews trip summaries at end of shift
- Uses insights to plan driving schedule
- Shares performance with fleet managers (if applicable)

## Stress Detection Algorithm

### Algorithm Overview

Our stress detection system uses a multi-layered approach that combines accelerometer and audio signals to identify potentially stressful driving conditions.

### Signal Processing Pipeline

#### 1. Accelerometer Analysis
```
Raw Accelerometer Data (ax, ay, az)
    ↓
Compute Horizontal Magnitude: √(ax² + ay²)
    ↓
Apply Savitzky-Golay Filter (window=11, polyorder=3)
    ↓
Detect Threshold Crossings:
    - Harsh Braking: < -2.0g
    - Harsh Acceleration: > 2.0g
    - Moderate Events: ±1.5g
    ↓
Extract Continuous Events (>0.5s duration)
    ↓
Calculate Confidence Scores
```

#### 2. Audio Analysis
```
Raw Audio Intensity (dB levels)
    ↓
Apply Exponential Moving Average (α=0.3)
    ↓
Detect Events:
    - Noise Spike: >80dB with >10dB increase
    - Sustained High: >70dB for >3s
    - Extreme Noise: >90dB
    ↓
Extract Continuous Events
    ↓
Calculate Confidence Scores
```

#### 3. Multi-Signal Fusion
```
Accelerometer Events + Audio Events
    ↓
Temporal Correlation (±5s window)
    ↓
Apply Fusion Rules:
    - Harsh Braking + Noise Spike → High Stress
    - Harsh Acceleration + Noise Spike → High Stress
    - Moderate Events + Noise → Medium Stress
    - Single High-Confidence Events → Low-Medium Stress
    ↓
Calculate Combined Confidence:
    Combined = (Accel_Conf × 0.6) + (Audio_Conf × 0.4)
    ↓
Classify Severity:
    - High: Combined > 0.8
    - Medium: Combined > 0.6
    - Low: Combined > 0.5
```

### Threshold Justification

#### Accelerometer Thresholds
- **Harsh Braking (-2.0g)**: Based on NHTSA standards for emergency braking
- **Harsh Acceleration (2.0g)**: Corresponds to rapid acceleration scenarios
- **Moderate Events (±1.5g)**: Elevated but non-emergency driving events

#### Audio Thresholds
- **Noise Spike (80dB)**: Equivalent to loud conversation or shouting
- **Sustained High (70dB)**: Level of raised voices or intense discussion
- **Extreme Noise (90dB)**: Shouting or conflict-level noise

### Confidence Scoring

Confidence scores are calculated based on:
- **Signal Strength**: How far the measurement exceeds the threshold
- **Duration**: Length of time above threshold
- **Consistency**: Stability of the signal during the event
- **Context**: Time of day and driving conditions

## Earnings Velocity Algorithm

### Algorithm Overview

The earnings velocity system calculates real-time earnings pace and predicts goal achievement probability using time-series analysis and machine learning.

### Velocity Calculation Pipeline

#### 1. Data Aggregation
```
Individual Earnings Updates
    ↓
Time-based Binning (15-minute intervals)
    ↓
Cumulative Earnings Calculation
    ↓
Time Elapsed Tracking
```

#### 2. Velocity Computation
```
Rolling Window Analysis (4-hour window)
    ↓
Calculate Earnings per Hour:
    Velocity = ΔEarnings / ΔTime
    ↓
Apply Exponential Smoothing:
    Smoothed_Velocity = EMA(Velocity, α=0.3)
    ↓
Trend Analysis:
    Trend = (Current_Velocity - Historical_Avg) / Historical_Avg
```

#### 3. Forecasting Model
```
Historical Velocity Patterns
    ↓
Linear Regression with Time Features:
    - Hour of Day
    - Day of Week
    - Recent Velocity
    - Velocity Trend
    ↓
Time-based Adjustments:
    - Peak Hours: ×1.3 multiplier
    - Off-Peak: ×0.8 multiplier
    ↓
Generate Forecast:
    Forecast_Earnings = Current_Earnings + (Adjusted_Velocity × Remaining_Hours)
```

#### 4. Goal Prediction
```
Current Progress + Forecast
    ↓
Calculate Achievement Probability:
    P(achieve) = min(1.0, Remaining_Time / Required_Time)
    ↓
Classify Status:
    - ON_TRACK: P > 0.8
    - AT_RISK: 0.5 ≤ P ≤ 0.8
    - LIKELY_MISSED: P < 0.5
    ↓
Generate Recommendations
```

### Cold Start Handling

For new drivers with limited data:
- **Default Velocity**: $15/hour based on city averages
- **Rapid Learning**: Update velocity every 30 minutes initially
- **Confidence Scaling**: Lower confidence for predictions with <2 hours of data
- **Hybrid Approach**: Combine personal data with city-wide averages

### Time-based Adjustments

#### Peak Hour Multipliers
- **Weekday Rush Hours (7-9 AM, 5-7 PM)**: ×1.3
- **Weekend Evenings (6-10 PM)**: ×1.2
- **Regular Daytime (10 AM-4 PM)**: ×1.1
- **Late Night (10 PM-6 AM)**: ×0.8

#### Environmental Factors
- **Weather**: Not implemented in MVP (future enhancement)
- **Traffic**: Implicitly captured through velocity patterns
- **Events**: Special events handled through anomaly detection

## Execution Strategy

### MVP Scope

#### Phase 1: Core Functionality (Week 1-2)
- [x] Data ingestion and cleaning
- [x] Basic signal processing
- [x] Simple event detection
- [x] Static dashboard with metrics

#### Phase 2: Advanced Features (Week 3-4)
- [x] Multi-signal fusion
- [x] Earnings velocity calculation
- [x] Goal prediction
- [x] Interactive dashboard

#### Phase 3: Polish & Optimization (Week 5-6)
- [x] Performance optimization
- [x] Error handling
- [x] Documentation
- [x] Deployment preparation

### Technical Implementation Strategy

#### 1. Modular Architecture
- Separate modules for each major component
- Clear interfaces between modules
- Comprehensive error handling
- Extensive logging and monitoring

#### 2. Data Processing Pipeline
- Batch processing for initial implementation
- Configurable processing windows
- Memory-efficient data handling
- Progress tracking and status reporting

#### 3. Dashboard Development
- Iterative design based on user feedback
- Responsive layout for different screen sizes
- Real-time updates where appropriate
- Export functionality for data

#### 4. Testing Strategy
- Unit tests for all core algorithms
- Integration tests for pipeline
- Performance tests for large datasets
- User acceptance testing for dashboard

## Trade-offs Between Precision vs Speed

### Design Decisions

#### 1. Algorithm Complexity
**Trade-off**: Rule-based vs Machine Learning
- **Chosen**: Rule-based with explicit thresholds
- **Reasoning**: 
  - Explainability is crucial for driver trust
  - Every detection can be traced to specific measurements
  - Drivers understand "braking at 2.2g" better than "model score 0.83"
  - Faster processing and lower computational requirements

#### 2. Signal Processing
**Trade-off**: Real-time vs Batch Processing
- **Chosen**: Batch processing with 15-minute windows
- **Reasoning**:
  - Reduces computational load
  - Provides more stable velocity calculations
  - Still delivers timely insights for drivers
  - Easier to implement and debug

#### 3. Model Accuracy
**Trade-off**: Simple vs Complex Forecasting
- **Chosen**: Linear regression with time adjustments
- **Reasoning**:
  - Sufficient accuracy for short-term predictions
  - Highly interpretable results
  - Fast computation
  - Less prone to overfitting with limited data

#### 4. Feature Engineering
**Trade-off**: Manual vs Automated Feature Selection
- **Chosen**: Manual feature selection based on domain expertise
- **Reasoning**:
  - Features are interpretable
  - Reduces risk of spurious correlations
  - Faster development cycle
  - Easier to maintain and debug

### Performance Considerations

#### Processing Speed Targets
- **Event Detection**: <100ms per trip
- **Velocity Calculation**: <50ms per driver
- **Dashboard Loading**: <3 seconds
- **Data Processing**: <5 minutes for full dataset

#### Memory Usage Targets
- **Peak Memory**: <500MB for typical datasets
- **Sustained Memory**: <200MB during normal operation
- **Memory Growth**: <10MB per hour of continuous operation

#### Accuracy Targets
- **Event Detection**: >85% precision, >80% recall
- **Velocity Prediction**: <10% mean absolute error
- **Goal Prediction**: >75% classification accuracy
- **False Positive Rate**: <5% for high-severity events

## Handling Noisy Sensor Data

### Noise Sources

#### 1. Accelerometer Noise
- **Vehicle Vibration**: Normal road vibration
- **Phone Movement**: Driver handling the phone
- **Sensor Drift**: Long-term calibration issues
- **Mounting Position**: Different orientations

#### 2. Audio Noise
- **Background Noise**: Traffic, music, conversations
- **Phone Calls**: Driver communication
- **Environmental Factors**: Car acoustics, window position
- **Audio Artifacts**: Microphone quality issues

### Noise Reduction Strategies

#### 1. Signal Filtering
```
Raw Signal
    ↓
Low-pass Filter (remove high-frequency noise)
    ↓
Band-pass Filter (focus on relevant frequencies)
    ↓
Moving Average (smooth short-term fluctuations)
    ↓
Savitzky-Golay Filter (preserve peaks while reducing noise)
```

#### 2. Statistical Methods
- **Outlier Detection**: Remove readings >3 standard deviations
- **Confidence Intervals**: Use statistical bounds for validation
- **Ensemble Methods**: Combine multiple detection approaches
- **Cross-validation**: Validate events across different time windows

#### 3. Contextual Filtering
- **Time-based Consistency**: Events must persist for minimum duration
- **Multi-signal Correlation**: Require confirmation from multiple sensors
- **Pattern Recognition**: Identify and ignore repetitive noise patterns
- **Adaptive Thresholds**: Adjust thresholds based on baseline noise levels

#### 4. Quality Assurance
- **Data Validation**: Check for sensor malfunctions
- **Calibration Routines**: Periodic sensor calibration
- **Quality Metrics**: Track signal quality over time
- **Fallback Mechanisms**: Graceful degradation when data quality is poor

### Specific Noise Handling

#### Potholes and Road Bumps
- **Detection**: Short-duration high-amplitude spikes
- **Filtering**: Ignore events <0.5 seconds duration
- **Classification**: Separate from actual braking events

#### Phone Drops and Movement
- **Detection**: Sudden orientation changes
- **Filtering**: Ignore events during phone movement
- **Recovery**: Resume normal processing after stabilization

#### Audio Interference
- **Detection**: Consistent background noise levels
- **Adaptation**: Adjust baseline noise thresholds
- **Isolation**: Focus on transient events over background

### Monitoring and Alerting

#### Quality Metrics
- **Signal-to-Noise Ratio**: Track SNR over time
- **Event Frequency**: Monitor for abnormal event rates
- **Threshold Violations**: Track how often thresholds are triggered
- **System Performance**: Monitor processing times and memory usage

#### Alert Conditions
- **High Noise Levels**: Alert when sensor noise exceeds acceptable levels
- **Sensor Malfunctions**: Detect and report sensor failures
- **Performance Degradation**: Alert when processing slows down
- **Data Quality Issues**: Flag unusual patterns in data quality

## Future Enhancements

### Advanced Signal Processing
- **Machine Learning**: Implement ML models for event detection
- **Deep Learning**: Use neural networks for pattern recognition
- **Sensor Fusion**: Incorporate GPS and gyroscope data
- **Real-time Processing**: Move from batch to real-time processing

### Enhanced Analytics
- **Predictive Analytics**: Predict likely events before they occur
- **Route Optimization**: Recommend optimal routes based on historical data
- **Weather Integration**: Incorporate weather data into predictions
- **Traffic Analysis**: Use real-time traffic data for insights

### User Experience Improvements
- **Mobile App**: Native mobile application for drivers
- **Push Notifications**: Real-time alerts for important events
- **Voice Interface**: Voice-activated commands and feedback
- **Gamification**: Add achievement systems and challenges

### System Scalability
- **Cloud Deployment**: Deploy to cloud infrastructure
- **Database Integration**: Replace CSV files with proper database
- **API Development**: RESTful API for third-party integrations
- **Microservices**: Break down into microservices architecture

---

**Document Version**: 1.0  
**Last Updated**: March 2026  
**Authors**: Team Velocity

## 1. Product Vision

### The Problem

A driver ends her 8-hour shift. The app shows one number: total earnings. She has no idea which hour was her most efficient, which trip exposed her to unusual risk, or whether her pace at 2pm was enough to hit her goal by 6pm. The data existed the whole time. It was just never surfaced.

### The Solution

Driver Pulse is a lightweight signal intelligence layer that sits between raw device/trip data and the driver's screen. It converts:

- **Motion sensors** → awareness of dangerous driving moments
- **Audio intensity** → awareness of cabin tension
- **Earnings records** → real-time goal pace tracking

It does not judge behaviour, surveil conversations, or create punitive records. It gives drivers the same situational awareness that a thoughtful co-pilot would have — but passively, respectfully, and automatically.

### Design Principles

1. **Driver-first framing.** Every flag is explained in language a driver would find useful, not algorithmic jargon.
2. **Privacy by construction.** Audio = dB levels only. No content. No voice. No transcripts.
3. **Explainable over accurate.** A rule-based system that a driver can understand is better than a black-box model that produces unexplained scores.
4. **Actionable, not alarming.** Flags should help drivers reflect and adjust — not create anxiety.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       DRIVER DEVICE (Edge)                  │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │ Accelerometer│   │  Microphone  │   │   Uber App     │  │
│  │  (10-50 Hz)  │   │ (dB only,    │   │ (trip events,  │  │
│  └──────┬───────┘   │  no content) │   │  fare updates) │  │
│         │           └──────┬───────┘   └───────┬────────┘  │
│         │                  │                   │           │
│         ▼                  ▼                   ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            SIGNAL PROCESSING MODULE (on-device)     │   │
│  │                                                     │   │
│  │  MotionDetector   AudioDetector   EarningsTracker   │   │
│  │       │                │                │           │   │
│  │       └────────────────┴────────────────┘           │   │
│  │                        │                            │   │
│  │               SignalFusion (conflict_moment)        │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                 │
│                    Real-time Alerts                         │
│                    (Driver UI overlay)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │  (post-trip sync)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       UBER CLOUD                            │
│                                                             │
│  ┌────────────────────┐    ┌──────────────────────────────┐ │
│  │  flagged_moments   │    │     driver_goals_enriched    │ │
│  │  trip_summaries    │    │     earnings_velocity_log    │ │
│  └────────────────────┘    └──────────────────────────────┘ │
│                                                             │
│              Driver Pulse Dashboard (Web/App)               │
└─────────────────────────────────────────────────────────────┘
```

### Edge vs Cloud Decision

| Processing | Location | Reason |
|-----------|---------|--------|
| Accelerometer feature extraction | Edge (device) | Low latency, works offline, privacy |
| Audio dB bucketing | Edge (device) | Never leaves device as content |
| Signal fusion (conflict_moment) | Edge (device) | Real-time in-trip alerting |
| Earnings velocity computation | Edge (device) | Driver needs this during the trip |
| Post-trip summaries | Cloud sync | Historical access, fleet analytics |
| Fleet-level dashboards | Cloud | Aggregated, not per-driver surveillance |

---

## 3. Algorithmic Design

### 3.1 Motion Signal Detection

**Feature extraction:**
```
horizontal_magnitude = sqrt(accel_x² + accel_y²)
```
We use horizontal magnitude (XY plane) only — this captures lateral forces (braking, swerving, acceleration) while ignoring vertical forces (road bumps, potholes) which are normal and uninformative.

**Classification rules:**

```
if magnitude >= 2.5 m/s²  →  harsh_braking   (motion_score = magnitude / 7.0, capped at 0.95)
if magnitude >= 1.8 m/s²  →  moderate_brake  (motion_score = magnitude / 5.0, capped at 0.75)
else                       →  normal (no event)
```

**Threshold justification:**
- ISA (Intelligent Speed Assistance) standards flag deceleration > 0.3g (~2.94 m/s²) as harsh. Our 2.5 threshold is slightly conservative to account for sensor noise on consumer phones.
- The moderate tier (1.8) catches elevated-but-not-extreme events. These alone don't create high-severity flags but contribute to combined scoring.

### 3.2 Audio Signal Detection

**Privacy-safe audio features used:**
- `audio_level_db` — aggregate cabin volume level
- `audio_classification` — pre-bucketed label (quiet/normal/conversation/loud/very_loud/argument)
- `sustained_duration_sec` — how long the elevated noise persisted

**Classification rules:**
```
if classification == "argument"               →  audio_spike (audio_score = dB / 100)
if dB >= 85 AND sustained_sec >= 20           →  audio_spike (high confidence)
if classification in ("very_loud", "loud")
   AND dB >= 70                               →  audio_spike (moderate confidence)
else                                           →  normal
```

**Why sustained duration matters:**
A single loud moment (door slam, horn) is not informative. A sustained 20+ second elevated audio level while the vehicle is in motion suggests ongoing cabin tension. This is the key de-noising step.

### 3.3 Signal Fusion

When a motion event and an audio event occur within a **120-second rolling window**, they are fused into a single `conflict_moment` or elevated flag:

```
combined_score = (motion_score × 0.55) + (audio_score × 0.45)

if combined_score >= 0.75  →  conflict_moment, severity = HIGH
if combined_score >= 0.55  →  motion flag type, severity = MEDIUM
else                        →  motion flag type, severity = LOW
```

**Why 55/45 weighting?**
Motion signals are more objective (physics-based) and harder to confuse. Audio can be elevated by radio, phone calls, or passenger conversations. Giving motion a slight edge reduces false positives while still allowing audio to push borderline motion events into high-severity.

**Why 120-second window?**
A conflict event (e.g., passengers arguing after a near-miss) may peak slightly after the triggering motion event. A 2-minute window is long enough to capture the cause-effect relationship without merging unrelated events from different trip phases.

### 3.4 Earnings Velocity Engine

```
current_velocity     = cumulative_earnings / elapsed_hours          (₹/hr)
remaining_hours      = target_hours - elapsed_hours
projected_end        = cumulative_earnings + (current_velocity × remaining_hours)

if projected_end >= target_earnings × 1.10  →  "ahead"
if projected_end >= target_earnings          →  "on_track"
else                                          →  "at_risk"
```

**Limitation and improvement path:**
The current model assumes constant velocity. In reality, surge pricing in morning/evening peaks creates non-linear earnings curves. A production implementation would use a rolling 30-minute velocity window to de-emphasise stale pace data, and optionally incorporate historical driver patterns from `avg_earnings_per_hour` as a Bayesian prior.

---

## 4. Stress Score Computation

The `stress_score` per trip is an aggregate summary for the post-trip report card:

```
if flagged_moments_count > 0:
    base_score   = mean(combined_score for all flags in this trip)
    count_boost  = min(flagged_moments_count × 0.05, 0.20)  # more flags = higher stress
    stress_score = min(base_score + count_boost, 0.99)
else:
    stress_score = uniform_random(0.03, 0.12)  # baseline ambient noise
```

Trip quality rating:
```
stress_score > 0.6   OR  max_severity == "high"    →  poor
stress_score > 0.35  OR  flagged_moments_count >= 2 →  fair
stress_score > 0.15  OR  flagged_moments_count >= 1 →  good
else                                                 →  excellent
```

---

## 5. Scalability Architecture

### How Driver Pulse scales from 1 city to 10M drivers

**The core tension:** Every driver generates continuous sensor streams. Naive cloud processing collapses under load. The solution is aggressive edge-first computation with minimal, structured cloud syncs.

#### Edge Compute Budget (Per Driver Device)
```
Accelerometer @ 10Hz = 10 readings/sec × 8 bytes = ~80 bytes/sec
Audio dB sampling @ 1Hz = ~4 bytes/sec
Output after edge processing: 0–3 flagged_moment records per trip (~1KB)
Compression ratio: ~5000x — raw sensor data never reaches cloud
```

#### Cloud Throughput at Scale
```
10M drivers × 5 trips/day × 1KB per trip = 50GB/day
= ~580KB/sec steady state  ← well within Kafka ingestion capacity
```

The bottleneck is **fan-out to fleet dashboards**, not ingestion. Solution: pre-aggregated Redis snapshots, not raw stream reads.

#### Streaming Architecture
```
DEVICE (edge, no network):
  Sensor poll → MotionDetector → AudioDetector → SignalFusion
  → In-trip: soft UI overlay only (no network I/O during trip)
  → Buffer flagged_moments in local SQLite

POST-TRIP SYNC (triggered at trip_end):
  Local buffer → gzip → POST /api/v1/trips/{id}/signals
  → Immediate trip quality card response to driver
  → Async Kafka pipeline for fleet aggregation

KAFKA TOPOLOGY:
  topic: driver.trips  (partitioned by city_id)
       │
  ┌────┴─────────────────────────┐
  │                              │
  Aggregation Service        Stream Processor
  (5-min materialized views   (real-time at-risk
   → Redis fleet stats)        alerts via WebSocket
                                to city ops)
```

#### Network Resilience
```
Driver enters dead zone mid-shift:
  ✓ Sensor processing continues (all edge)
  ✓ Earnings velocity updates from local fare events
  ✓ Flagged moments queued in SQLite with retry

On reconnect (exponential backoff, max 30min):
  1. Flush buffered signals (idempotency key = trip_id + timestamp)
  2. Sync goal checkpoint (server reconciles)
  3. Pull updated shift targets

Server behaviour while driver offline:
  → No action (stateless between syncs)
  → Fleet dashboard shows "pending sync" not "error"
  → No false at-risk alerts from missing data
```

---

## 6. Key Design Tradeoffs

### Tradeoff 1: Rule-Based vs ML Detection

| | Rule-Based (chosen) | ML Alternative |
|---|---|---|
| Explainability | ✅ Every flag traceable to threshold | ❌ Opaque score |
| Data requirement | ✅ Works with 30 trips | ❌ Needs 10,000+ labelled trips |
| Driver trust | ✅ "dB > 85 for 30s" | ❌ "Model says 0.83" |
| Latency | ✅ <1ms | ⚠️ 5–50ms inference |
| Accuracy ceiling | ⚠️ Bounded by threshold design | ✅ Learns complex patterns |

**Path forward:** Once we have 50K+ labelled events with driver feedback, migrate to a gradient-boosted classifier as a second-pass filter on top of existing rules.

### Tradeoff 2: Edge vs Cloud Processing

| | Edge (chosen) | Cloud |
|---|---|---|
| Privacy | ✅ Audio never leaves device | ❌ Raw streams uploaded |
| Offline reliability | ✅ Works in tunnels | ❌ Dead without network |
| Latency | ✅ Real-time, zero RTT | ❌ 200–500ms roundtrip |
| Battery | ⚠️ ~2% extra/hr for sensor polling | ✅ Offloads compute |
| Model updates | ⚠️ Requires SDK push | ✅ Server-side only |

**Verdict:** Privacy and offline reliability are non-negotiable for a driver safety tool.

### Tradeoff 3: Constant Velocity vs Rolling Window Earnings Forecast

| | Constant Velocity (current) | 30-min Rolling Window |
|---|---|---|
| Simplicity | ✅ Deterministic, easy to explain | ⚠️ Time-series buffer needed |
| Early-shift accuracy | ❌ High variance (few trips) | ✅ Adapts quickly |
| Surge capture | ❌ Misses ramp-up pattern | ✅ Weights recent earnings |

**Current mitigation:** Forecast suppressed until 2+ trips or 45+ min elapsed.
**Production recommendation:** Rolling window with exponential decay (α = 0.3).

### Tradeoff 4: Real-Time Alerts vs Post-Trip Reflection

We **explicitly chose post-trip only for conflict moments**. A real-time "⚠️ Conflict detected!" alert creates a secondary distraction at the exact moment a driver needs full attention on the road. The safety cost of distraction outweighs the benefit of the alert.

**Exception — passive real-time signals (no sound, no animation):**
- Earnings pace bar (visible at-a-glance)
- Trip quality indicator (readable at traffic stops)

Harsh braking, audio spikes, conflict moments: **post-trip reflection only**.

---

## 7. MVP Execution Strategy

### Phase 1 (Hackathon — Complete)
- Rule-based signal pipeline on historical dataset
- Post-trip summary dashboard (fleet + per-driver views)
- Earnings goal tracker with velocity + projection

### Phase 2 (Production MVP — Next 6 weeks)
- Port pipeline to Kotlin/Swift for on-device execution
- Integrate with live Uber trip event stream
- Real-time in-trip overlay: "Rough moment detected — drive safe"
- Earnings bar in app: "You're ₹340/hr — your target is ₹200/hr ✓"

### Phase 3 (V2 — Longer term)
- Rolling velocity window (30-min) for more accurate mid-shift projection
- Historical pattern learning: "You usually earn 20% more between 5–7pm — worth staying on"
- Opt-in weekly report: "Your calmest trip this week vs your most stressful"
- Fleet safety analytics (aggregated, privacy-preserving) for city ops teams

---

## 8. Why Rule-Based, Not ML?

The brief explicitly notes: *"Rule-based systems, heuristics, and simple predictive logic are completely acceptable."*

We chose rule-based detection for three reasons:

1. **Explainability.** Every flag can be directly traced to a threshold crossing. A driver can be shown exactly why a moment was flagged — not "the model assigned a score of 0.83."

2. **Data constraints.** The sensor dataset covers only 30 trips with sparse readings (4–22 rows per trip). This is insufficient to train a reliable classifier without severe overfitting.

3. **Trust.** A system that affects how drivers perceive their own safety should be auditable. A rule that says "we flagged this because your cabin audio was above 85dB for 30 consecutive seconds" is auditable. A neural network is not.

If sensor data were richer (sub-second resolution across thousands of trips), a lightweight model (isolation forest for anomaly detection, or a 3-layer LSTM on the time series) would be appropriate — but only if it improved precision on a held-out validation set and we could explain its decisions.

---

## 9. Data Constraints & Honest Notes

| Constraint | Detail |
|-----------|--------|
| Sensor coverage | 30 of 220 trips have accelerometer/audio readings. 190 trips have 0 detectable events — this is a dataset limitation, not a detection failure. |
| Audio is pre-classified | The `audio_classification` column is pre-labelled in the dataset. In production, on-device bucketing (energy-based, no content) would replace this. |
| Sparse sensor readings | 4–22 readings per trip vs the 10Hz that a real device would produce. Events between readings are undetectable. |
| Single-day dataset | All data is from 2024-02-06. No longitudinal patterns can be learned. |
