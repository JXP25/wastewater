"""
Real-Time Prediction Service for Wastewater Treatment
Consumes sensor data from Kafka → LSTM Model → Predictions
"""

import os
import json
import time
import logging
from collections import deque
from datetime import datetime
import numpy as np
import tensorflow as tf
from kafka import KafkaConsumer
import psycopg2
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURATION
# ==========================================
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka:29092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'wastewater-sensors')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'prediction-service')

MODEL_PATH = os.getenv('MODEL_PATH', '/app/lstm/model/best_model.keras')
SCALER_PATH = os.getenv('SCALER_PATH', '/app/lstm/model/scalers.npz')

DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'wastewater')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

# LSTM requires 120 time steps (10 hours of 5-minute intervals)
TIME_STEPS = 120
PREDICTION_INTERVAL = 5  # Make prediction every 5 messages (every 5 seconds if IoT sends every 1s)

# Feature mapping from IoT simulator to model inputs
# Model expects: turbidity, flow_rate, ph, do, temp, fan_speed (aeration_vfd_speed)
FEATURE_MAPPING = [
    'turbidity_ntu',
    'flow_rate_m3h', 
    'ph',
    'dissolved_oxygen_mgl',
    'temperature_c',
    'aeration_vfd_speed_pct'  # fan_speed_control equivalent
]

TARGET_NAMES = ['TSS', 'COD', 'BOD']

# ==========================================
# MODEL & DATABASE INITIALIZATION
# ==========================================
class PredictionService:
    def __init__(self):
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
        self.data_buffer = deque(maxlen=TIME_STEPS)
        self.message_count = 0
        self.prediction_count = 0
        self.db_conn = None
        
        self._load_model()
        self._load_scalers()
        self._init_database()
        
    def _load_model(self):
        """Load the trained LSTM model"""
        logger.info(f"Loading LSTM model from {MODEL_PATH}...")
        try:
            self.model = tf.keras.models.load_model(MODEL_PATH)
            logger.info("✓ Model loaded successfully")
            logger.info(f"  Input shape: {self.model.input_shape}")
            logger.info(f"  Output shape: {self.model.output_shape}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_scalers(self):
        """Load MinMaxScaler parameters"""
        logger.info(f"Loading scalers from {SCALER_PATH}...")
        try:
            scalers = np.load(SCALER_PATH)
            
            # Reconstruct scalers from saved min/max
            from sklearn.preprocessing import MinMaxScaler
            
            self.scaler_X = MinMaxScaler()
            self.scaler_X.data_min_ = scalers['scaler_X_min']
            self.scaler_X.data_max_ = scalers['scaler_X_max']
            self.scaler_X.scale_ = 1.0 / (self.scaler_X.data_max_ - self.scaler_X.data_min_)
            self.scaler_X.min_ = -self.scaler_X.data_min_ * self.scaler_X.scale_
            self.scaler_X.feature_range = (0, 1)
            self.scaler_X.n_features_in_ = len(self.scaler_X.data_min_)
            self.scaler_X.n_samples_seen_ = 1
            
            self.scaler_y = MinMaxScaler()
            self.scaler_y.data_min_ = scalers['scaler_y_min']
            self.scaler_y.data_max_ = scalers['scaler_y_max']
            self.scaler_y.scale_ = 1.0 / (self.scaler_y.data_max_ - self.scaler_y.data_min_)
            self.scaler_y.min_ = -self.scaler_y.data_min_ * self.scaler_y.scale_
            self.scaler_y.feature_range = (0, 1)
            self.scaler_y.n_features_in_ = len(self.scaler_y.data_min_)
            self.scaler_y.n_samples_seen_ = 1
            
            logger.info("✓ Scalers loaded successfully")
            logger.info(f"  Features: {self.scaler_X.n_features_in_}")
            logger.info(f"  Targets: {self.scaler_y.n_features_in_}")
        except Exception as e:
            logger.error(f"Failed to load scalers: {e}")
            raise
    
    def _init_database(self):
        """Initialize PostgreSQL database connection and create table"""
        logger.info("Connecting to PostgreSQL database...")
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.db_conn = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD
                )
                self.db_conn.autocommit = True
                logger.info("✓ Connected to database")
                
                # Create predictions table
                with self.db_conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS predictions (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP NOT NULL,
                            tss_mg_l REAL NOT NULL,
                            cod_mg_l REAL NOT NULL,
                            bod_mg_l REAL NOT NULL,
                            model_version VARCHAR(50) DEFAULT 'lstm_v1',
                            inference_time_ms REAL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
                        ON predictions(timestamp DESC);
                    """)
                logger.info("✓ Database table ready")
                return
                
            except psycopg2.OperationalError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Failed to connect to database after {max_retries} attempts")
                    raise
                logger.warning(f"Database not ready, retrying ({retry_count}/{max_retries})...")
                time.sleep(2)
    
    def _extract_features(self, message):
        """Extract feature vector from Kafka message"""
        try:
            data = json.loads(message.value.decode('utf-8'))
            
            # Data is nested under 'sensors' and 'control_actions'
            sensors = data.get('sensors', {})
            control_actions = data.get('control_actions', {})
            
            # Combine into single dict for lookup
            all_data = {**sensors, **control_actions}
            
            # Extract features in correct order
            features = []
            for feature_name in FEATURE_MAPPING:
                if feature_name in all_data:
                    features.append(float(all_data[feature_name]))
                else:
                    logger.warning(f"Missing feature: {feature_name}, using 0.0")
                    features.append(0.0)
            
            return np.array(features)
        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return None
    
    def _make_prediction(self):
        """Generate prediction from buffered data"""
        if len(self.data_buffer) < TIME_STEPS:
            logger.debug(f"Buffer not full yet: {len(self.data_buffer)}/{TIME_STEPS}")
            return None
        
        try:
            start_time = time.time()
            
            # Convert buffer to numpy array
            X_raw = np.array(list(self.data_buffer))  # Shape: (TIME_STEPS, n_features)
            
            # Scale features
            X_scaled = self.scaler_X.transform(X_raw)
            
            # Reshape for LSTM: (1, TIME_STEPS, n_features)
            X_seq = X_scaled.reshape(1, TIME_STEPS, -1)
            
            # Predict
            y_pred_scaled = self.model.predict(X_seq, verbose=0)
            
            # Inverse transform to get actual values
            y_pred = self.scaler_y.inverse_transform(y_pred_scaled)[0]
            
            inference_time = (time.time() - start_time) * 1000  # milliseconds
            
            prediction = {
                'timestamp': datetime.utcnow().isoformat(),
                'tss_mg_l': float(y_pred[0]),
                'cod_mg_l': float(y_pred[1]),
                'bod_mg_l': float(y_pred[2]),
                'inference_time_ms': round(inference_time, 2)
            }
            
            self.prediction_count += 1
            
            logger.info(
                f"🎯 Prediction #{self.prediction_count} | "
                f"TSS: {prediction['tss_mg_l']:.2f} mg/L | "
                f"COD: {prediction['cod_mg_l']:.2f} mg/L | "
                f"BOD: {prediction['bod_mg_l']:.2f} mg/L | "
                f"Inference: {inference_time:.2f}ms"
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None
    
    def _save_prediction(self, prediction):
        """Save prediction to database"""
        if not prediction or not self.db_conn:
            return
        
        try:
            with self.db_conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO predictions 
                    (timestamp, tss_mg_l, cod_mg_l, bod_mg_l, inference_time_ms)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        prediction['timestamp'],
                        prediction['tss_mg_l'],
                        prediction['cod_mg_l'],
                        prediction['bod_mg_l'],
                        prediction['inference_time_ms']
                    )
                )
            logger.debug("✓ Prediction saved to database")
        except Exception as e:
            logger.error(f"Failed to save prediction: {e}")
    
    def run(self):
        """Main processing loop"""
        logger.info(f"Starting Prediction Service...")
        logger.info(f"  Kafka Broker: {KAFKA_BROKER}")
        logger.info(f"  Topic: {KAFKA_TOPIC}")
        logger.info(f"  Time Steps Required: {TIME_STEPS}")
        logger.info(f"  Prediction Interval: Every {PREDICTION_INTERVAL} messages")
        
        # Connect to Kafka
        max_retries = 30
        retry_count = 0
        consumer = None
        
        while retry_count < max_retries and consumer is None:
            try:
                consumer = KafkaConsumer(
                    KAFKA_TOPIC,
                    bootstrap_servers=KAFKA_BROKER,
                    group_id=KAFKA_GROUP_ID,
                    auto_offset_reset='latest',  # Start from latest messages
                    enable_auto_commit=True,
                    value_deserializer=lambda m: m
                )
                logger.info("✓ Connected to Kafka")
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logger.error(f"Failed to connect to Kafka after {max_retries} attempts")
                    raise
                logger.warning(f"Kafka not ready, retrying ({retry_count}/{max_retries})...")
                time.sleep(2)
        
        logger.info("="*70)
        logger.info("🚀 Prediction Service Ready - Waiting for sensor data...")
        logger.info("="*70)
        
        # Process messages
        try:
            for message in consumer:
                self.message_count += 1
                
                # Extract features
                features = self._extract_features(message)
                if features is None:
                    continue
                
                # Add to buffer
                self.data_buffer.append(features)
                
                # Make prediction at intervals
                if self.message_count % PREDICTION_INTERVAL == 0:
                    prediction = self._make_prediction()
                    if prediction:
                        self._save_prediction(prediction)
                
                # Status update every 50 messages
                if self.message_count % 50 == 0:
                    buffer_status = f"{len(self.data_buffer)}/{TIME_STEPS}"
                    logger.info(
                        f"📊 Status | Messages: {self.message_count} | "
                        f"Predictions: {self.prediction_count} | "
                        f"Buffer: {buffer_status}"
                    )
                    
        except KeyboardInterrupt:
            logger.info("\nShutting down gracefully...")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
        finally:
            if consumer:
                consumer.close()
            if self.db_conn:
                self.db_conn.close()
            logger.info("✓ Service stopped")

# ==========================================
# MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    # Force CPU for inference (faster startup, consistent performance)
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    
    service = PredictionService()
    service.run()
