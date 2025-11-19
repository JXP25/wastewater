# IoT Device Simulator

Simulates real-time sensor data from a Wastewater Treatment Plant (WTP) and streams it to Apache Kafka.

## Purpose

Generates realistic sensor readings and control actions that mimic a real wastewater treatment plant's operational data. This provides continuous input data for the ML prediction service.

## Data Generated

### Environmental Sensors (6)
- **Turbidity** (NTU) - Measures water cloudiness
- **Flow Rate** (m³/h) - Influent water volume
- **pH** - Acidity/alkalinity level
- **Temperature** (°C) - Water temperature
- **Dissolved Oxygen** (mg/L) - Oxygen concentration
- **Conductivity** (µS/cm) - Electrical conductivity

### Control Actions (4)
- **Aeration VFD Speed** (%) - Blower speed control
- **Polymer Dosing Rate** (L/h) - Chemical dosing
- **RAS Pump Speed** (%) - Return activated sludge pump
- **WAS Pump Rate** (m³/h) - Waste activated sludge pump

## Features

- **Realistic Patterns**: Daily load cycles with morning/evening peaks
- **Sensor Noise**: Adds realistic variability to readings
- **Temporal Correlation**: Sensors respond realistically to each other
- **Kafka Streaming**: Publishes JSON messages to Kafka topic

## Configuration

Environment variables:
- `KAFKA_SERVER`: Kafka broker address (default: kafka:29092)
- `KAFKA_TOPIC`: Topic name (default: wastewater-sensors)
- `INTERVAL`: Seconds between messages (default: 1)
- `PLANT_ID`: Plant identifier (default: WTP-001)

## Message Format

```json
{
  "plant_id": "WTP-001",
  "timestamp": "2025-11-19T12:00:00",
  "sensors": {
    "turbidity_ntu": 65.3,
    "flow_rate_m3h": 720.5,
    "ph": 7.2,
    "temperature_c": 20.1,
    "dissolved_oxygen_mgl": 7.8,
    "conductivity_uscm": 850.2
  },
  "control_actions": {
    "aeration_vfd_speed_pct": 75.0,
    "polymer_dosing_rate_lh": 18.5,
    "ras_pump_speed_pct": 70.0,
    "was_pump_rate_m3h": 30.0
  },
  "metadata": {
    "device_status": "online",
    "data_quality": "good",
    "hrt_hours": 6.0,
    "tank_volume_m3": 4675.0,
    "process_stage": "activated_sludge",
    "ml_ready": true
  }
}
```

## Running Standalone

```bash
python iot_simulator.py \
  --kafka-server localhost:9092 \
  --kafka-topic wastewater-sensors \
  --daily-pattern \
  --interval 1
```

## Dependencies

- numpy - Numerical operations
- kafka-python - Kafka client library
