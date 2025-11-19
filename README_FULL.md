# Wastewater Treatment Plant - Real-Time Prediction System

**Replace 48-hour lab tests with sub-second algorithmic predictions using LSTM and real-time sensor data.**

## 🎯 Goal

Replace traditional 48-hour lab tests (TSS, COD, BOD) with real-time ML predictions, enabling:
- **Sub-second predictions** instead of 2-day wait times
- **Proactive control** of treatment processes
- **Cost reduction** in lab operations
- **Improved effluent quality** through immediate feedback

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────┐      ┌──────────────────┐      ┌─────────────┐
│  IoT Sensors    │─────▶│  Kafka   │─────▶│ Prediction       │─────▶│  Database   │
│  (Simulated)    │      │ Streaming│      │ Service (LSTM)   │      │ (PostgreSQL)│
└─────────────────┘      └──────────┘      └──────────────────┘      └─────────────┘
                                                                              │
                                                                              ▼
                                                                       ┌─────────────┐
                                                                       │ REST API    │
                                                                       │ (Flask)     │
                                                                       └─────────────┘
                                                                              │
                                                                              ▼
                                                                       ┌─────────────┐
                                                                       │   Control   │
                                                                       │   System    │
                                                                       └─────────────┘
```

## 📊 System Components

### 1. **Data Ingestion Layer**
- **IoT Simulator**: Generates realistic sensor data (6 parameters)
  - Turbidity, Flow Rate, pH, Temperature, DO, Conductivity
  - Daily load patterns (morning/evening peaks)
  - Control actions (aeration, polymer dosing, pump speeds)

### 2. **Streaming Platform**
- **Apache Kafka**: High-throughput, fault-tolerant message broker
- **Kafka UI**: Web-based monitoring interface

### 3. **ML Prediction Service**
- **LSTM Model**: Trained on 6 months of historical data (51,840 samples)
- **Time-Series Input**: 10-hour lookback window (120 time steps)
- **Predictions**: TSS, COD, BOD in mg/L
- **Performance**: Sub-second inference (~50ms)
- **Accuracy**: R² > 0.5 on all targets

### 4. **Data Storage**
- **PostgreSQL**: Stores predictions with timestamps
- **Indexed queries**: Fast retrieval for API

### 5. **API Layer**
- **REST API**: Low-latency endpoint for control systems
- **Endpoints**:
  - `GET /api/v1/predictions/latest` - Most recent prediction
  - `GET /api/v1/predictions/history` - Historical predictions
  - `GET /api/v1/statistics` - Aggregated statistics

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB+ RAM available
- Ports available: 5000, 5432, 8080, 9092

### One-Command Deployment

```bash
# Start entire system
docker compose up -d

# View logs (all services)
docker compose logs -f

# View specific service
docker compose logs -f prediction-service

# Check service health
curl http://localhost:5000/health
```

### Services & Ports
- **API Service**: http://localhost:5000
- **Kafka UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432
- **Kafka**: localhost:9092

## 📈 Model Performance

| Target | R² Score | MAE (mg/L) | RMSE (mg/L) |
|--------|----------|------------|-------------|
| TSS    | 0.5585   | 2.161      | 3.143       |
| COD    | 0.5320   | 4.316      | 6.915       |
| BOD    | 0.5206   | 0.326      | 0.435       |

**Training Details:**
- 51,840 samples (6 months, 5-min intervals)
- TIME_STEPS: 120 (10-hour lookback)
- Architecture: 2-layer LSTM (64→32 units)
- Training time: ~20 minutes (CPU)

## 🔧 API Usage Examples

### Get Latest Prediction
```bash
curl http://localhost:5000/api/v1/predictions/latest
```

Response:
```json
{
  "timestamp": "2025-11-19T12:30:00",
  "predictions": {
    "tss_mg_l": 8.45,
    "cod_mg_l": 32.18,
    "bod_mg_l": 2.76
  },
  "metadata": {
    "inference_time_ms": 47.3,
    "created_at": "2025-11-19T12:30:00.123"
  }
}
```

### Get Historical Predictions
```bash
curl "http://localhost:5000/api/v1/predictions/history?hours=24&limit=100"
```

### Get Statistics
```bash
curl "http://localhost:5000/api/v1/statistics?hours=24"
```

## 📁 Project Structure

```
wastewater/
├── docker-compose.yml          # Complete system orchestration
├── iot_simulator.py            # IoT sensor data generator
├── prediction_service.py       # ML inference microservice
├── api_service.py              # REST API server
├── Dockerfile                  # IoT simulator container
├── Dockerfile.prediction       # Prediction service container
├── Dockerfile.api              # API service container
├── requirements*.txt           # Python dependencies
└── lstm/
    ├── generate_training_data.py
    ├── train_lstm_model.py
    ├── training_data_6months.csv
    └── model/
        ├── best_model.keras    # Trained LSTM model
        ├── scalers.npz         # Feature scalers
        └── training_history.json
```

## 🎓 Training New Models

```bash
# Generate training data
cd lstm
python generate_training_data.py

# Train LSTM model
python train_lstm_model.py

# Rebuild prediction service with new model
docker compose up -d --build prediction-service
```

## 📊 Monitoring

### Kafka UI
Visit http://localhost:8080 to monitor:
- Message throughput
- Consumer lag
- Topic health

### Database Queries
```bash
# Connect to PostgreSQL
docker exec -it wastewater-postgres psql -U postgres -d wastewater

# View recent predictions
SELECT * FROM predictions ORDER BY timestamp DESC LIMIT 10;

# Get hourly statistics
SELECT 
  DATE_TRUNC('hour', timestamp) as hour,
  AVG(tss_mg_l) as avg_tss,
  AVG(cod_mg_l) as avg_cod,
  AVG(bod_mg_l) as avg_bod
FROM predictions
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;
```

## 🛠️ Troubleshooting

### Services not starting
```bash
# Check service logs
docker compose logs <service-name>

# Restart specific service
docker compose restart <service-name>
```

### No predictions appearing
1. Check IoT simulator is sending data: `docker compose logs iot-simulator`
2. Verify Kafka connectivity: Visit http://localhost:8080
3. Check prediction service buffer status: `docker compose logs prediction-service`

### Database connection issues
```bash
# Verify PostgreSQL is healthy
docker compose ps postgres

# Check database logs
docker compose logs postgres
```

## 🔄 Development Workflow

### Modify IoT Simulator
```bash
# Edit iot_simulator.py
# Rebuild and restart
docker compose up -d --build iot-simulator
```

### Update Prediction Service
```bash
# Edit prediction_service.py
# Rebuild and restart
docker compose up -d --build prediction-service
```

### Update API
```bash
# Edit api_service.py
# Rebuild and restart
docker compose up -d --build api-service
```

## 📝 Configuration

### Environment Variables

**IoT Simulator:**
- `KAFKA_SERVER`: Kafka broker address
- `KAFKA_TOPIC`: Target topic name
- `INTERVAL`: Message interval (seconds)

**Prediction Service:**
- `KAFKA_BROKER`: Kafka broker address
- `DB_HOST`: PostgreSQL host
- `MODEL_PATH`: Path to LSTM model
- `SCALER_PATH`: Path to scalers

**API Service:**
- `DB_HOST`: PostgreSQL host
- `DB_PORT`: PostgreSQL port

## 🎯 Production Checklist

- [ ] Add authentication to API (JWT/OAuth)
- [ ] Implement rate limiting
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure database backups
- [ ] Add alerting for prediction anomalies
- [ ] Implement model versioning
- [ ] Add CI/CD pipeline
- [ ] Security audit
- [ ] Load testing
- [ ] Documentation for operators

## 📄 License

MIT License

## 🤝 Contributing

Contributions welcome! Please submit pull requests or open issues.
