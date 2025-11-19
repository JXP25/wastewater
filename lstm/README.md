# LSTM Model Training - Wastewater Treatment Prediction

## Overview
This folder contains the training data and scripts for building an LSTM model to predict effluent quality (TSS, COD, BOD) from real-time sensor data.

## Training Data

### Dataset: `training_data_6months.csv`
- **Size**: 51,840 samples (6 months of data)
- **Sampling Interval**: 5 minutes
- **File Size**: ~7.37 MB
- **Date Range**: April 1, 2025 - September 28, 2025

### Data Structure

#### Input Features (7 variables with temporal offsets)

| Feature | Description | Time Offset | Unit | Range |
|---------|-------------|-------------|------|-------|
| `turbidity_influent_t_minus_10h` | Influent turbidity | t-10h | NTU | 15-115 |
| `flow_rate_influent_t_minus_10h` | Influent flow rate | t-10h | m³/h | 100-854 |
| `temp_influent_t_minus_10h` | Influent temperature | t-10h | °C | 15-25 |
| `ph_aeration_basin_t_minus_5h` | Aeration basin pH | t-5h | - | 6.8-7.6 |
| `do_aeration_basin_t_minus_5h` | Dissolved oxygen | t-5h | mg/L | 0.5-4.0 |
| `fan_speed_control_t_minus_5h` | Aeration fan speed | t-5h | % | 40-95 |
| `timestamp_effluent` | Measurement timestamp | t | ISO8601 | - |

#### Target Variables (3 effluent quality parameters)

| Target | Description | Unit | Range | Regulatory Limit |
|--------|-------------|------|-------|------------------|
| `tss_effluent_mgL` | Total Suspended Solids | mg/L | 2-15 | < 30 mg/L |
| `cod_effluent_mgL` | Chemical Oxygen Demand | mg/L | 15-50 | < 125 mg/L |
| `bod_effluent_mgL` | Biochemical Oxygen Demand | mg/L | 2-8 | < 30 mg/L |

### Temporal Offset Explanation

The temporal offsets reflect the **Hydraulic Retention Time (HRT)** of the treatment process:

- **t-10h**: Influent sensors measure wastewater entering the plant. Due to the ~10-hour HRT, this water will affect effluent quality 10 hours later.
- **t-5h**: Aeration basin measurements (pH, DO) and control actions (fan speed) occur midway through treatment, affecting effluent in 5 hours.
- **t**: Effluent quality measurements (TSS, COD, BOD) - what we want to predict.

```
Timeline:
t-10h: Water enters → [Influent sensors]
t-5h:  Water in treatment → [Aeration sensors + Control actions]
t:     Water exits → [Effluent quality measurements] ← PREDICT THIS
```

## Data Generation

### Script: `generate_training_data.py`

The data generator creates realistic synthetic data with:

✅ **Physical Correlations**
- Higher influent load (turbidity × flow) → poorer treatment → higher effluent values
- Better aeration (fan speed, DO) → better treatment → lower effluent values
- Optimal pH (~7.25) → better biological activity → lower effluent values

✅ **Temporal Patterns**
- **Daily cycles**: Morning peak (6-9 AM), evening peak (5-8 PM), night low (11 PM-5 AM)
- **Weekly cycles**: Lower flows on weekends
- **Operator response**: Fan speed adjusts to load and DO levels

✅ **Realistic Noise**
- Sensor measurement uncertainty
- Process variability
- Random drift over time

### Feature Correlations

From the generated data:

| Feature | TSS | COD | BOD |
|---------|-----|-----|-----|
| Turbidity (influent) | -0.25 | -0.40 | -0.54 |
| Flow Rate (influent) | -0.32 | -0.43 | -0.54 |
| pH (aeration) | -0.10 | -0.15 | -0.20 |
| DO (aeration) | +0.12 | +0.21 | +0.34 |
| Temperature | -0.33 | -0.25 | -0.12 |
| **Fan Speed** | **-0.46** | **-0.56** | **-0.67** |

**Key Insight**: Fan speed (aeration control) has the strongest correlation with effluent quality, making it a critical feature for the LSTM model.

## Usage

### Generate Training Data
```bash
cd /home/jxp/Desktop/wastewater/lstm
source ~/tf311/bin/activate
python generate_training_data.py
```

### Load Data for Training
```python
import pandas as pd

# Load data
df = pd.read_csv('training_data_6months.csv')

# Convert timestamp
df['timestamp_effluent'] = pd.to_datetime(df['timestamp_effluent'])

# Split features and targets
X = df[[
    'turbidity_influent_t_minus_10h',
    'flow_rate_influent_t_minus_10h',
    'ph_aeration_basin_t_minus_5h',
    'do_aeration_basin_t_minus_5h',
    'temp_influent_t_minus_10h',
    'fan_speed_control_t_minus_5h'
]]

y = df[[
    'tss_effluent_mgL',
    'cod_effluent_mgL',
    'bod_effluent_mgL'
]]
```

## LSTM Model Requirements

### Sequence Length
For time-series LSTM, we need to create sequences based on HRT:
- **Lookback window**: 10 hours (to capture influent data)
- **Samples per sequence**: 120 (10 hours × 12 samples/hour at 5-min intervals)

### Train/Validation/Test Split
Recommended split for time-series:
- **Training**: First 70% (April - July, ~36,000 samples)
- **Validation**: Next 15% (August, ~7,800 samples)
- **Test**: Last 15% (September, ~7,800 samples)

**Important**: Use temporal split (not random) to avoid data leakage!

### Expected Model Architecture
```
Input: (batch_size, 120 timesteps, 6 features)
       ↓
LSTM Layer 1: 64 units
       ↓
Dropout: 0.2
       ↓
LSTM Layer 2: 32 units
       ↓
Dropout: 0.2
       ↓
Dense: 3 outputs (TSS, COD, BOD)
```

## Next Steps

1. ✅ **Training data generated** - 51,840 samples ready
2. ⏳ **Data preprocessing** - Normalize features, create sequences
3. ⏳ **Model architecture** - Build LSTM network
4. ⏳ **Training** - Train on historical data
5. ⏳ **Validation** - Evaluate on unseen test data
6. ⏳ **Deployment** - Integrate with Kafka streaming

## File Structure

```
lstm/
├── generate_training_data.py     # Data generator script
├── training_data_6months.csv     # Generated training data (51,840 samples)
├── README.md                      # This file
└── (future files)
    ├── preprocess_data.py         # Normalization and sequencing
    ├── train_lstm_model.py        # Model training script
    ├── model/                     # Saved model weights
    └── evaluate_model.py          # Performance evaluation
```

## References

- Hydraulic Retention Time (HRT): Typical 4-8 hours for activated sludge
- Regulatory limits: US EPA Secondary Treatment Standards
- LSTM for time-series: Suitable for temporal dependencies in treatment processes
