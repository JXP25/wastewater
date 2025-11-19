# Wastewater Treatment Plant - Real-Time Prediction System

## Goal
Replace the 48-hour lab test with sub-second algorithmic predictions using real-time sensor data and machine learning.

## System Architecture

```
IoT Devices (PLCs) → Kafka Streaming → ML Prediction Service → API/Database → WTP Control System
```

### Components

1. **IoT Device Simulator** (`iot_simulator.py`)
   - Simulates 6 real-time sensors:
     - Turbidity (NTU)
     - Flow Rate (m³/h)
     - pH
     - Temperature (°C)
     - Dissolved Oxygen (mg/L)
     - Conductivity (μS/cm)

2. **Streaming Platform** (Apache Kafka)
   - Decouples data producers from consumers
   - Ensures fault tolerance and high throughput

3. **ML Prediction Service** (Coming next)
   - LSTM-based model for time-series prediction
   - Predicts TSS, COD, and BOD values
   - Sub-second inference time

4. **Database & API** (Coming next)
   - Low-latency storage and retrieval
   - gRPC API for WTP control systems

## Getting Started

### Prerequisites
- Docker & Docker Compose v2
- (Optional) Python 3.11+ with TensorFlow environment for local development

### 🚀 Quick Start - ONE COMMAND!

```bash
./setup_kafka.sh
```

**That's it!** This single command will:
1. Build the IoT simulator Docker image
2. Start Kafka, Zookeeper, Kafka UI, and IoT Simulator
3. Begin streaming real-time sensor data to Kafka automatically

### Verify It's Working

#### View Kafka UI (Recommended)
Open http://localhost:8080 in your browser to see:
- Topics and messages in real-time
- Consumer groups
- Broker health

#### View Simulator Logs
```bash
./view_simulator_logs.sh
# or
docker compose logs -f iot-simulator
```

#### Consume Messages with Python
```bash
./consume_kafka.sh
```

### Manual Installation

If you want to run without Kafka:
```bash
# Activate TensorFlow environment
source ~/tf311/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run simulator without Kafka (console output only)
python iot_simulator.py
```

### Advanced Usage

#### Generate Training Dataset (File Output)
```bash
source ~/tf311/bin/activate
python iot_simulator.py --duration 3600 --interval 1 --output-file training_data.jsonl --daily-pattern
```

#### Run with Custom Settings
```bash
./run_with_kafka.sh --interval 0.5 --anomaly
```

#### Stop Kafka Services
```bash
docker-compose down
```

### Command Line Options

- `--plant-id`: Plant identifier (default: WTP-001)
- `--interval`: Sampling interval in seconds (default: 1.0)
- `--duration`: Duration in seconds (default: infinite)
- `--kafka-topic`: Kafka topic name (default: wastewater-sensors)
- `--kafka-server`: Kafka bootstrap server (default: localhost:9092)
- `--output-file`: Output file for data logging
- `--daily-pattern`: Enable daily usage pattern simulation
- `--anomaly`: Enable anomaly generation

### Docker Services

The `docker-compose.yml` file includes:
- **Kafka**: Message broker at `localhost:9092`
- **Zookeeper**: Kafka coordination service at `localhost:2181`
- **Kafka UI**: Web interface at `http://localhost:8080` for monitoring topics, messages, and consumers

### Project Structure

```
wastewater/
├── docker-compose.yml          # Complete stack: Kafka + IoT Simulator
├── Dockerfile                  # IoT simulator container image
├── setup_kafka.sh              # ONE-COMMAND setup script
├── view_simulator_logs.sh      # View simulator output
├── consume_kafka.sh            # Python Kafka consumer
├── run_with_kafka.sh           # Run simulator locally (alternative)
├── iot_simulator.py            # Main IoT device simulator
├── test_simulator.py           # Quick test script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Docker Services (All in docker-compose.yml)

- **Kafka** (port 9092): Message broker
- **Zookeeper** (port 2181): Kafka coordination
- **Kafka UI** (port 8080): Web interface for monitoring
- **IoT Simulator**: Continuously streams sensor data to Kafka

### Managing Services

```bash
# Start everything
./setup_kafka.sh

# Stop everything
docker compose down

# View all logs
docker compose logs -f

# Restart just the simulator
docker compose restart iot-simulator

# Stop simulator (keep Kafka running)
docker compose stop iot-simulator

# Start simulator again
docker compose start iot-simulator
```

## Next Steps

1. ✅ **IoT Device Simulator** - Streaming real-time sensor data
2. ✅ **Historical Data Generator** - 51,840 samples with TSS, COD, BOD labels
3. ⏳ **Data Preprocessing Pipeline** - Normalization and sequence creation
4. ⏳ **LSTM Model Training** - Build and train prediction model
5. ⏳ **Real-time Prediction Service** - Deploy model as microservice
6. ⏳ **Kafka Consumer Implementation** - Buffer time-series data
7. ⏳ **API Service (gRPC)** - Low-latency prediction endpoint
8. ⏳ **Database Integration** - Store predictions and historical data

## Example Output

```json
{
  "plant_id": "WTP-001",
  "timestamp": "2025-11-19T10:30:45.123456",
  "sensors": {
    "turbidity_ntu": 52.34,
    "flow_rate_m3h": 485.67,
    "ph": 7.18,
    "temperature_c": 21.5,
    "dissolved_oxygen_mgl": 6.42,
    "conductivity_uscm": 795.23
  },
  "metadata": {
    "device_status": "online",
    "data_quality": "good"
  }
}
```
