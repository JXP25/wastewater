# Wastewater Treatment Plant ML Prediction System# Wastewater Treatment Plant - Real-Time Prediction System



Real-time water quality prediction system that replaces 48-hour lab tests with sub-second ML predictions (99.99% faster).## Goal

Replace the 48-hour lab test with sub-second algorithmic predictions using real-time sensor data and machine learning.

## 🎯 Overview

## System Architecture

This system uses IoT sensors, Apache Kafka streaming, and LSTM neural networks to provide real-time predictions of wastewater effluent quality parameters. The architecture enables treatment plant operators to make immediate process adjustments instead of waiting 2 days for lab results.

```

### Key MetricsIoT Devices (PLCs) → Kafka Streaming → ML Prediction Service → API/Database → WTP Control System

- **Prediction Time**: ~100ms (vs 48-hour lab tests)```

- **Speed Improvement**: 99.99% faster

- **Model Performance**: R² > 0.5 for all parameters### Components

- **Deployment**: Single command (`docker compose up`)

1. **IoT Device Simulator** (`iot_simulator.py`)

## 🏗️ Architecture   - Simulates 6 real-time sensors:

     - Turbidity (NTU)

```     - Flow Rate (m³/h)

┌─────────────────┐     - pH

│  IoT Sensors    │ → 6 environmental sensors     - Temperature (°C)

│  (Simulator)    │   + 4 control actions     - Dissolved Oxygen (mg/L)

└────────┬────────┘     - Conductivity (μS/cm)

         │ Kafka Topic

         │ (wastewater-sensors)2. **Streaming Platform** (Apache Kafka)

         ▼   - Decouples data producers from consumers

┌─────────────────┐   - Ensures fault tolerance and high throughput

│  Prediction     │ → LSTM Model (120 timesteps)

│  Service        │   TSS, COD, BOD predictions3. **ML Prediction Service** (Coming next)

└────────┬────────┘   - LSTM-based model for time-series prediction

         │ PostgreSQL   - Predicts TSS, COD, and BOD values

         │ (predictions table)   - Sub-second inference time

         ▼

┌─────────────────┐4. **Database & API** (Coming next)

│  REST API       │ → /api/v1/predictions/latest   - Low-latency storage and retrieval

│  Service        │   /api/v1/statistics   - gRPC API for WTP control systems

└─────────────────┘

```## Getting Started



## 🚀 Quick Start### Prerequisites

- Docker & Docker Compose v2

### Prerequisites- (Optional) Python 3.11+ with TensorFlow environment for local development

- Docker & Docker Compose

- 8GB RAM (for all services)### 🚀 Quick Start - ONE COMMAND!

- Ports available: 5000, 8080, 5432, 9092

```bash

### Deploy System./setup_kafka.sh

```

```bash

# Start all services (Kafka, PostgreSQL, IoT simulator, ML service, API)**That's it!** This single command will:

docker compose up -d1. Build the IoT simulator Docker image

2. Start Kafka, Zookeeper, Kafka UI, and IoT Simulator

# Verify services are running3. Begin streaming real-time sensor data to Kafka automatically

docker compose ps

### Verify It's Working

# Check API health

curl http://localhost:5000/health#### View Kafka UI (Recommended)

```Open http://localhost:8080 in your browser to see:

- Topics and messages in real-time

### Access Services- Consumer groups

- **REST API**: http://localhost:5000- Broker health

- **Kafka UI**: http://localhost:8080

- **PostgreSQL**: localhost:5432 (user: postgres, password: postgres)#### View Simulator Logs

```bash

## 📊 Get Predictions./view_simulator_logs.sh

# or

```bashdocker compose logs -f iot-simulator

# Get latest prediction```

curl http://localhost:5000/api/v1/predictions/latest

#### Consume Messages with Python

# Get last 100 predictions```bash

curl http://localhost:5000/api/v1/predictions/history?limit=100./consume_kafka.sh

```

# Get daily statistics

curl http://localhost:5000/api/v1/statistics?hours=24### Manual Installation

```

If you want to run without Kafka:

**Example Response:**```bash

```json# Activate TensorFlow environment

{source ~/tf311/bin/activate

  "timestamp": "2025-11-19T12:00:00",

  "predictions": {# Install Python dependencies

    "tss_mg_l": 8.09,pip install -r requirements.txt

    "cod_mg_l": 41.17,

    "bod_mg_l": 2.17# Run simulator without Kafka (console output only)

  },python iot_simulator.py

  "metadata": {```

    "inference_time_ms": 100.45

  }### Advanced Usage

}

```#### Generate Training Dataset (File Output)

```bash

## 🧩 Servicessource ~/tf311/bin/activate

python iot_simulator.py --duration 3600 --interval 1 --output-file training_data.jsonl --daily-pattern

### 1. [IoT Simulator](./iot-simulator/README.md)```

Generates realistic WTP sensor data with daily load patterns and streams to Kafka.

- 6 environmental sensors (turbidity, flow, pH, DO, temperature, conductivity)#### Run with Custom Settings

- 4 control actions (aeration, polymer dosing, RAS/WAS pumps)```bash

- 1 message/second with realistic noise and correlations./run_with_kafka.sh --interval 0.5 --anomaly

```

### 2. [Prediction Service](./prediction-service/README.md)

ML inference microservice consuming Kafka stream and storing predictions.#### Stop Kafka Services

- LSTM model (2-layer: 64→32 units)```bash

- 120 timestep lookback (10 hours)docker-compose down

- Predicts TSS, COD, BOD in ~100ms```

- Automatic scaling and batching

### Command Line Options

### 3. [API Service](./api-service/README.md)

Low-latency REST API for accessing predictions.- `--plant-id`: Plant identifier (default: WTP-001)

- Flask + Gunicorn (2 workers)- `--interval`: Sampling interval in seconds (default: 1.0)

- Latest predictions, history, statistics- `--duration`: Duration in seconds (default: infinite)

- CORS-enabled for web integration- `--kafka-topic`: Kafka topic name (default: wastewater-sensors)

- Designed for SCADA/PLC integration- `--kafka-server`: Kafka bootstrap server (default: localhost:9092)

- `--output-file`: Output file for data logging

## 📁 Project Structure- `--daily-pattern`: Enable daily usage pattern simulation

- `--anomaly`: Enable anomaly generation

```

wastewater/### Docker Services

├── docker-compose.yml          # Complete system orchestration

├── DEPLOYMENT_COMPLETE.md      # Deployment metrics & validationThe `docker-compose.yml` file includes:

│- **Kafka**: Message broker at `localhost:9092`

├── iot-simulator/              # IoT device simulator- **Zookeeper**: Kafka coordination service at `localhost:2181`

│   ├── iot_simulator.py        # Sensor data generator- **Kafka UI**: Web interface at `http://localhost:8080` for monitoring topics, messages, and consumers

│   ├── Dockerfile

│   ├── requirements.txt### Project Structure

│   └── README.md

│```

├── prediction-service/         # ML inference servicewastewater/

│   ├── prediction_service.py   # LSTM prediction pipeline├── docker-compose.yml          # Complete stack: Kafka + IoT Simulator

│   ├── Dockerfile├── Dockerfile                  # IoT simulator container image

│   ├── requirements.txt├── setup_kafka.sh              # ONE-COMMAND setup script

│   └── README.md├── view_simulator_logs.sh      # View simulator output

│├── consume_kafka.sh            # Python Kafka consumer

├── api-service/                # REST API├── run_with_kafka.sh           # Run simulator locally (alternative)

│   ├── api_service.py          # Flask API endpoints├── iot_simulator.py            # Main IoT device simulator

│   ├── Dockerfile├── test_simulator.py           # Quick test script

│   ├── requirements.txt├── requirements.txt            # Python dependencies

│   └── README.md└── README.md                   # This file

│```

└── lstm/                       # ML model artifacts

    ├── model/### Docker Services (All in docker-compose.yml)

    │   ├── best_model.keras    # Trained LSTM model

    │   ├── scalers.npz         # Feature/target scalers- **Kafka** (port 9092): Message broker

    │   └── training_history.json- **Zookeeper** (port 2181): Kafka coordination

    ├── plots/- **Kafka UI** (port 8080): Web interface for monitoring

    │   ├── training_history.png- **IoT Simulator**: Continuously streams sensor data to Kafka

    │   └── predictions_test.png

    ├── training_data_6months.csv### Managing Services

    └── train_lstm_model.py

``````bash

# Start everything

## 🧪 Model Performance./setup_kafka.sh



### Training Dataset# Stop everything

- **Samples**: 51,840 (6 months of simulated data)docker compose down

- **Interval**: 5 minutes

- **Features**: 6 (turbidity, flow, pH, DO, temperature, aeration speed)# View all logs

- **Targets**: 3 (TSS, COD, BOD)docker compose logs -f



### Performance Metrics# Restart just the simulator

| Parameter | R² Score | MAE (mg/L) | RMSE (mg/L) |docker compose restart iot-simulator

|-----------|----------|------------|-------------|

| TSS       | 0.5585   | 2.161      | 2.852       |# Stop simulator (keep Kafka running)

| COD       | 0.5320   | 4.316      | 5.718       |docker compose stop iot-simulator

| BOD       | 0.5206   | 0.326      | 0.433       |

# Start simulator again

### Real-World Impactdocker compose start iot-simulator

- **48-hour lab test** → **100ms prediction** (1,728,000x faster)```

- Enables real-time process control

- Reduces operational costs (fewer lab samples needed)## Next Steps

- Improves effluent quality through faster adjustments

1. ✅ **IoT Device Simulator** - Streaming real-time sensor data

## 🔧 Configuration2. ✅ **Historical Data Generator** - 51,840 samples with TSS, COD, BOD labels

3. ⏳ **Data Preprocessing Pipeline** - Normalization and sequence creation

### Environment Variables4. ⏳ **LSTM Model Training** - Build and train prediction model

All services configured via docker-compose.yml:5. ⏳ **Real-time Prediction Service** - Deploy model as microservice

6. ⏳ **Kafka Consumer Implementation** - Buffer time-series data

**Kafka Configuration:**7. ⏳ **API Service (gRPC)** - Low-latency prediction endpoint

- Bootstrap servers: kafka:290928. ⏳ **Database Integration** - Store predictions and historical data

- Topic: wastewater-sensors

- Consumer group: prediction-service## Example Output



**PostgreSQL Configuration:**```json

- Host: postgres:5432{

- Database: wastewater  "plant_id": "WTP-001",

- User/Password: postgres/postgres  "timestamp": "2025-11-19T10:30:45.123456",

  "sensors": {

**API Configuration:**    "turbidity_ntu": 52.34,

- Port: 5000    "flow_rate_m3h": 485.67,

- Workers: 2    "ph": 7.18,

- Timeout: 60s    "temperature_c": 21.5,

    "dissolved_oxygen_mgl": 6.42,

## 🛠️ Development    "conductivity_uscm": 795.23

  },

### Training a New Model  "metadata": {

    "device_status": "online",

```bash    "data_quality": "good"

cd lstm/  }

}

# Generate training data (6 months)```

python generate_training_data.py --months 6 --output training_data_6months.csv

# Train LSTM model
python train_lstm_model.py \
  --data training_data_6months.csv \
  --epochs 100 \
  --batch-size 64 \
  --time-steps 120

# Model saved to: model/best_model.keras
# Scalers saved to: model/scalers.npz
```

### Monitoring System

```bash
# View all service logs
docker compose logs -f

# View specific service
docker compose logs -f prediction-service

# Check Kafka messages
docker compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic wastewater-sensors \
  --from-beginning

# Query database directly
docker compose exec postgres psql -U postgres -d wastewater \
  -c "SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 5;"
```

### Stopping System

```bash
# Stop all services
docker compose down

# Stop and remove volumes (caution: deletes data)
docker compose down -v
```

## 📈 Use Cases

1. **Real-Time Process Control**
   - Immediate feedback for aeration adjustments
   - Optimize chemical dosing based on predictions
   - Prevent effluent violations before they occur

2. **Operational Efficiency**
   - Reduce lab testing costs
   - Enable 24/7 monitoring without staff
   - Faster response to influent changes

3. **Compliance & Reporting**
   - Continuous effluent quality tracking
   - Historical trend analysis via API
   - Automated alerting for predicted violations

4. **Research & Optimization**
   - Test control strategies in simulation
   - Evaluate process modifications
   - Validate operational best practices

## 🤝 Integration

### SCADA/PLC Integration
```python
import requests
import time

# Poll API every 5 seconds
while True:
    response = requests.get('http://localhost:5000/api/v1/predictions/latest')
    prediction = response.json()['predictions']
    
    # Send to PLC via Modbus/OPC UA
    write_to_plc('tss_predicted', prediction['tss_mg_l'])
    write_to_plc('cod_predicted', prediction['cod_mg_l'])
    
    time.sleep(5)
```

### Dashboard Integration
The API provides CORS-enabled endpoints suitable for:
- Grafana dashboards
- Custom React/Vue/Angular apps
- Power BI reports
- Excel data connections

## 📝 License

This is a demonstration system for wastewater treatment ML prediction capabilities.

## 🚨 Important Notes

- **IoT Simulator**: Currently generates synthetic data. Replace with real PLC/SCADA integration for production.
- **Model Retraining**: Retrain periodically with actual plant data to maintain accuracy.
- **Database Scaling**: Current PostgreSQL setup suitable for single plant. Consider TimescaleDB for multi-plant deployments.
- **Security**: Add authentication (JWT/OAuth) before exposing API to internet.

## 📚 Additional Documentation

- [IoT Simulator Details](./iot-simulator/README.md)
- [Prediction Service Details](./prediction-service/README.md)
- [API Service Details](./api-service/README.md)
- [Deployment Metrics](./DEPLOYMENT_COMPLETE.md)

---

**Built with**: Python 3.11, TensorFlow 2.20, Apache Kafka, PostgreSQL, Flask, Docker
