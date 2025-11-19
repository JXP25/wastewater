# Prediction Service

ML microservice that consumes real-time sensor data from Kafka, runs LSTM inference, and stores predictions in PostgreSQL.

## Purpose

Provides sub-second predictions of water quality parameters (TSS, COD, BOD) using a trained LSTM neural network, replacing traditional 48-hour lab tests with real-time algorithmic predictions.

## How It Works

1. **Consumes** sensor data from Kafka topic `wastewater-sensors`
2. **Buffers** last 120 time steps (10 hours of data)
3. **Predicts** effluent quality parameters using LSTM model
4. **Stores** predictions in PostgreSQL database

## Model Architecture

- **Type**: LSTM (Long Short-Term Memory) neural network
- **Lookback Window**: 120 time steps (10 hours at 5-min intervals)
- **Architecture**: 2-layer LSTM (64→32 units) + Dense layers
- **Input Features** (6):
  - Turbidity (NTU)
  - Flow Rate (m³/h)
  - pH
  - Dissolved Oxygen (mg/L)
  - Temperature (°C)
  - Aeration VFD Speed (%)

- **Output Predictions** (3):
  - TSS - Total Suspended Solids (mg/L)
  - COD - Chemical Oxygen Demand (mg/L)
  - BOD - Biochemical Oxygen Demand (mg/L)

## Performance

- **Inference Time**: ~100ms (sub-second)
- **Model Accuracy**:
  - TSS: R² = 0.5585, MAE = 2.161 mg/L
  - COD: R² = 0.5320, MAE = 4.316 mg/L
  - BOD: R² = 0.5206, MAE = 0.326 mg/L

## Configuration

Environment variables:
- `KAFKA_BROKER`: Kafka broker address (default: kafka:29092)
- `KAFKA_TOPIC`: Input topic (default: wastewater-sensors)
- `KAFKA_GROUP_ID`: Consumer group (default: prediction-service)
- `DB_HOST`: PostgreSQL host (default: postgres)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name (default: wastewater)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: postgres)
- `MODEL_PATH`: Path to LSTM model file
- `SCALER_PATH`: Path to feature scalers file

## Database Schema

```sql
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    tss_mg_l REAL NOT NULL,
    cod_mg_l REAL NOT NULL,
    bod_mg_l REAL NOT NULL,
    model_version VARCHAR(50) DEFAULT 'lstm_v1',
    inference_time_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Prediction Frequency

Makes a prediction every 5 messages received (configurable via `PREDICTION_INTERVAL` constant).

## Model Files Required

- `lstm/model/best_model.keras` - Trained LSTM model
- `lstm/model/scalers.npz` - MinMaxScaler parameters (features and targets)

These files are mounted as a volume from the host system.

## Dependencies

- tensorflow - LSTM model inference
- numpy - Numerical operations
- kafka-python - Kafka consumer
- psycopg2-binary - PostgreSQL client
- scikit-learn - Data scaling (MinMaxScaler)
