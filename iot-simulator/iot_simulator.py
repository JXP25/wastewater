"""
IoT Device Simulator for Wastewater Treatment Plant
Simulates real-time sensor data from PLCs (Programmable Logic Controllers)
Sensors: Turbidity, Flow Rate, pH, Temperature, Dissolved Oxygen, Conductivity
"""

import json
import time
import random
import numpy as np
from datetime import datetime
from typing import Dict, List
import argparse
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SensorSimulator:
    """Base class for sensor simulation with realistic variations"""
    
    def __init__(self, name: str, base_value: float, std_dev: float, 
                 min_val: float, max_val: float, drift_rate: float = 0.0):
        self.name = name
        self.base_value = base_value
        self.std_dev = std_dev
        self.min_val = min_val
        self.max_val = max_val
        self.drift_rate = drift_rate
        self.current_drift = 0.0
        self.anomaly_mode = False
        
    def read(self) -> float:
        """Generate a realistic sensor reading with noise and drift"""
        # Add random walk drift
        self.current_drift += np.random.normal(0, self.drift_rate)
        self.current_drift = np.clip(self.current_drift, -self.base_value * 0.2, self.base_value * 0.2)
        
        # Generate reading with noise
        if self.anomaly_mode:
            # Simulate anomalies (10% chance of spike)
            if random.random() < 0.1:
                noise_factor = random.uniform(2, 4)
            else:
                noise_factor = 1
        else:
            noise_factor = 1
            
        reading = self.base_value + self.current_drift + np.random.normal(0, self.std_dev * noise_factor)
        
        # Clip to realistic bounds
        return np.clip(reading, self.min_val, self.max_val)
    
    def set_anomaly_mode(self, enabled: bool):
        """Enable/disable anomaly generation"""
        self.anomaly_mode = enabled


class WastewaterPlantSimulator:
    """Simulates a complete wastewater treatment plant with multiple sensors and control actions"""
    
    def __init__(self, plant_id: str = "WTP-001"):
        self.plant_id = plant_id
        
        # Initialize environmental sensors with realistic parameters for wastewater treatment
        self.sensors = {
            # Turbidity (NTU - Nephelometric Turbidity Units)
            'turbidity': SensorSimulator(
                name='Turbidity',
                base_value=50.0,
                std_dev=5.0,
                min_val=0.0,
                max_val=1000.0,
                drift_rate=0.5
            ),
            
            # Flow Rate (m³/hour)
            'flow_rate': SensorSimulator(
                name='Flow Rate',
                base_value=500.0,
                std_dev=50.0,
                min_val=100.0,
                max_val=2000.0,
                drift_rate=5.0
            ),
            
            # pH (0-14 scale)
            'ph': SensorSimulator(
                name='pH',
                base_value=7.2,
                std_dev=0.3,
                min_val=5.0,
                max_val=9.0,
                drift_rate=0.02
            ),
            
            # Temperature (°C)
            'temperature': SensorSimulator(
                name='Temperature',
                base_value=20.0,
                std_dev=1.5,
                min_val=5.0,
                max_val=35.0,
                drift_rate=0.1
            ),
            
            # Dissolved Oxygen (mg/L)
            'dissolved_oxygen': SensorSimulator(
                name='Dissolved Oxygen',
                base_value=6.5,
                std_dev=0.5,
                min_val=0.0,
                max_val=15.0,
                drift_rate=0.05
            ),
            
            # Conductivity (μS/cm)
            'conductivity': SensorSimulator(
                name='Conductivity',
                base_value=800.0,
                std_dev=80.0,
                min_val=100.0,
                max_val=3000.0,
                drift_rate=10.0
            )
        }
        
        # Initialize control actions/actuator settings
        # These represent the operational state of the treatment plant
        self.actuators = {
            # Aeration system - VFD speed control (0-100%)
            'aeration_vfd_speed': SensorSimulator(
                name='Aeration VFD Speed',
                base_value=65.0,
                std_dev=3.0,
                min_val=0.0,
                max_val=100.0,
                drift_rate=0.5
            ),
            
            # Polymer dosing rate (L/h)
            'polymer_dosing_rate': SensorSimulator(
                name='Polymer Dosing Rate',
                base_value=15.0,
                std_dev=2.0,
                min_val=0.0,
                max_val=50.0,
                drift_rate=0.3
            ),
            
            # Return Activated Sludge (RAS) pump speed (%)
            'ras_pump_speed': SensorSimulator(
                name='RAS Pump Speed',
                base_value=70.0,
                std_dev=5.0,
                min_val=0.0,
                max_val=100.0,
                drift_rate=0.8
            ),
            
            # Waste Activated Sludge (WAS) pump rate (m³/h)
            'was_pump_rate': SensorSimulator(
                name='WAS Pump Rate',
                base_value=25.0,
                std_dev=3.0,
                min_val=0.0,
                max_val=100.0,
                drift_rate=0.4
            )
        }
        
        # Hydraulic Retention Time (HRT) - typical for activated sludge process
        self.hrt_hours = 6.0  # Time for water to pass through the treatment system
        
    def read_all_sensors(self) -> Dict:
        """Read all sensors, actuators, and return formatted data with metadata"""
        timestamp = datetime.now().isoformat()
        flow_rate = self.sensors['flow_rate'].read()
        
        # Calculate current tank volume based on flow and HRT
        # V = Q * HRT (where Q is flow rate, HRT is retention time)
        tank_volume_m3 = flow_rate * self.hrt_hours
        
        data = {
            'plant_id': self.plant_id,
            'timestamp': timestamp,
            
            # Environmental sensor readings (Input Features for ML)
            'sensors': {
                'turbidity_ntu': round(self.sensors['turbidity'].read(), 2),
                'flow_rate_m3h': round(flow_rate, 2),
                'ph': round(self.sensors['ph'].read(), 2),
                'temperature_c': round(self.sensors['temperature'].read(), 2),
                'dissolved_oxygen_mgl': round(self.sensors['dissolved_oxygen'].read(), 2),
                'conductivity_uscm': round(self.sensors['conductivity'].read(), 2)
            },
            
            # Control actions/actuator settings (Additional Input Features for ML)
            'control_actions': {
                'aeration_vfd_speed_pct': round(self.actuators['aeration_vfd_speed'].read(), 2),
                'polymer_dosing_rate_lh': round(self.actuators['polymer_dosing_rate'].read(), 2),
                'ras_pump_speed_pct': round(self.actuators['ras_pump_speed'].read(), 2),
                'was_pump_rate_m3h': round(self.actuators['was_pump_rate'].read(), 2)
            },
            
            # System metadata for ML model (temporal context)
            'metadata': {
                'device_status': 'online',
                'data_quality': 'good',
                'hrt_hours': self.hrt_hours,  # Critical for LSTM lookback window
                'tank_volume_m3': round(tank_volume_m3, 2),
                'process_stage': 'activated_sludge',
                'ml_ready': True  # Indicates data is ready for ML consumption
            }
        }
        
        return data
    
    def simulate_daily_pattern(self, hour: int):
        """Adjust sensor and actuator base values based on time of day (peak usage patterns)"""
        # Morning peak (6-9 AM) - High influent load
        if 6 <= hour <= 9:
            flow_multiplier = 1.4
            turbidity_multiplier = 1.3
            aeration_multiplier = 1.2  # Increase aeration for higher load
            dosing_multiplier = 1.15
        # Evening peak (5-8 PM) - Highest influent load
        elif 17 <= hour <= 20:
            flow_multiplier = 1.5
            turbidity_multiplier = 1.4
            aeration_multiplier = 1.3
            dosing_multiplier = 1.2
        # Night low activity (11 PM - 5 AM) - Minimal influent
        elif hour >= 23 or hour <= 5:
            flow_multiplier = 0.6
            turbidity_multiplier = 0.7
            aeration_multiplier = 0.8  # Reduce aeration to save energy
            dosing_multiplier = 0.7
        else:
            flow_multiplier = 1.0
            turbidity_multiplier = 1.0
            aeration_multiplier = 1.0
            dosing_multiplier = 1.0
            
        # Adjust environmental sensors
        self.sensors['flow_rate'].base_value = 500.0 * flow_multiplier
        self.sensors['turbidity'].base_value = 50.0 * turbidity_multiplier
        
        # Adjust control actions (operators respond to load changes)
        self.actuators['aeration_vfd_speed'].base_value = 65.0 * aeration_multiplier
        self.actuators['polymer_dosing_rate'].base_value = 15.0 * dosing_multiplier


class KafkaProducerSimulator:
    """Simulates sending data to Kafka (can be replaced with actual Kafka producer)"""
    
    def __init__(self, topic: str = "wastewater-sensors", bootstrap_servers: str = "localhost:9092"):
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.use_real_kafka = False
        
        # Try to import kafka-python
        try:
            from kafka import KafkaProducer
            logger.info(f"Connecting to Kafka at {bootstrap_servers}...")
            self.producer = KafkaProducer(
                bootstrap_servers=[bootstrap_servers],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1)
            )
            self.use_real_kafka = True
            logger.info(f"✓ Connected to Kafka at {bootstrap_servers}")
            logger.info(f"✓ Publishing to topic: {topic}")
        except ImportError:
            logger.warning("⚠ kafka-python not installed. Running in simulation mode.")
            logger.warning("  Install with: pip install kafka-python")
            self.producer = None
        except Exception as e:
            logger.error(f"⚠ Could not connect to Kafka: {e}")
            logger.warning("  Running in simulation mode.")
            self.producer = None
    
    def send(self, data: Dict):
        """Send data to Kafka or print to console"""
        if self.use_real_kafka and self.producer:
            try:
                future = self.producer.send(self.topic, value=data)
                # Wait for send to complete (optional)
                record_metadata = future.get(timeout=10)
                logger.info(
                    f"✓ Sent to Kafka topic '{self.topic}' "
                    f"[partition: {record_metadata.partition}, offset: {record_metadata.offset}] "
                    f"- Turbidity: {data['sensors']['turbidity_ntu']:.2f} NTU, "
                    f"Flow: {data['sensors']['flow_rate_m3h']:.2f} m³/h"
                )
            except Exception as e:
                logger.error(f"✗ Error sending to Kafka: {e}")
                logger.debug(json.dumps(data, indent=2))
        else:
            # Simulation mode - print to console
            logger.info(f"[SIMULATION MODE] {json.dumps(data)}")
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()


def main():
    parser = argparse.ArgumentParser(description='IoT Device Simulator for Wastewater Treatment Plant')
    parser.add_argument('--plant-id', type=str, default='WTP-001', help='Plant ID identifier')
    parser.add_argument('--interval', type=float, default=1.0, help='Sampling interval in seconds')
    parser.add_argument('--duration', type=int, default=None, help='Duration in seconds (None = infinite)')
    parser.add_argument('--kafka-topic', type=str, default='wastewater-sensors', help='Kafka topic name')
    parser.add_argument('--kafka-server', type=str, default='localhost:9092', help='Kafka bootstrap server')
    parser.add_argument('--output-file', type=str, default=None, help='Output file for data logging')
    parser.add_argument('--daily-pattern', action='store_true', help='Simulate daily usage patterns')
    parser.add_argument('--anomaly', action='store_true', help='Enable anomaly generation')
    
    args = parser.parse_args()
    
    # Initialize simulator
    plant = WastewaterPlantSimulator(plant_id=args.plant_id)
    kafka_producer = KafkaProducerSimulator(topic=args.kafka_topic, bootstrap_servers=args.kafka_server)
    
    # Enable anomalies if requested
    if args.anomaly:
        for sensor in plant.sensors.values():
            sensor.set_anomaly_mode(True)
        logger.warning("⚠ Anomaly mode enabled")
    
    # Open output file if specified
    output_file = None
    if args.output_file:
        output_file = open(args.output_file, 'w')
        logger.info(f"✓ Logging data to {args.output_file}")
    
    logger.info("="*60)
    logger.info("  Wastewater Treatment Plant IoT Simulator")
    logger.info(f"  Plant ID: {args.plant_id}")
    logger.info(f"  Sampling Interval: {args.interval}s")
    logger.info(f"  Daily Pattern: {'Enabled' if args.daily_pattern else 'Disabled'}")
    logger.info(f"  Duration: {'Infinite' if not args.duration else f'{args.duration}s'}")
    logger.info("="*60)
    
    start_time = time.time()
    sample_count = 0
    
    try:
        logger.info("Starting data collection...")
        while True:
            # Simulate daily patterns
            if args.daily_pattern:
                current_hour = datetime.now().hour
                plant.simulate_daily_pattern(current_hour)
            
            # Read sensors
            data = plant.read_all_sensors()
            
            # Send to Kafka
            kafka_producer.send(data)
            
            # Log to file
            if output_file:
                output_file.write(json.dumps(data) + '\n')
                output_file.flush()
            
            sample_count += 1
            
            # Check duration
            if args.duration and (time.time() - start_time) >= args.duration:
                logger.info("Duration limit reached")
                break
            
            # Wait for next sample
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logger.info("\n" + "="*60)
        logger.info("  Simulation stopped by user")
        logger.info(f"  Total samples: {sample_count}")
        logger.info(f"  Duration: {time.time() - start_time:.2f}s")
        logger.info("="*60)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        logger.info("Shutting down...")
        kafka_producer.close()
        if output_file:
            output_file.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    main()
