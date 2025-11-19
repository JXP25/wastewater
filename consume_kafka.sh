#!/bin/bash
# Simple Kafka consumer to view messages

source ~/tf311/bin/activate

echo "Kafka Consumer - Wastewater Sensors"
echo "Topic: wastewater-sensors"
echo "Press Ctrl+C to stop"
echo ""

python -c "
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'wastewater-sensors',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print('✓ Connected to Kafka')
print('Waiting for messages...\n')

for message in consumer:
    data = message.value
    sensors = data['sensors']
    print(f\"[{data['timestamp']}] Plant: {data['plant_id']}\")
    print(f\"  Turbidity: {sensors['turbidity_ntu']:.2f} NTU\")
    print(f\"  Flow Rate: {sensors['flow_rate_m3h']:.2f} m³/h\")
    print(f\"  pH: {sensors['ph']:.2f}\")
    print(f\"  Temperature: {sensors['temperature_c']:.2f} °C\")
    print(f\"  DO: {sensors['dissolved_oxygen_mgl']:.2f} mg/L\")
    print(f\"  Conductivity: {sensors['conductivity_uscm']:.2f} μS/cm\")
    print()
"
