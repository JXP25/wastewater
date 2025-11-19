"""
gRPC API Service for Wastewater Treatment Predictions
Serves low-latency predictions to WTP Control System
"""

import os
import logging
import psycopg2
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'wastewater')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

app = Flask(__name__)
CORS(app)

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'wastewater-api',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/api/v1/predictions/latest', methods=['GET'])
def get_latest_prediction():
    """Get the most recent prediction"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    timestamp,
                    tss_mg_l,
                    cod_mg_l,
                    bod_mg_l,
                    inference_time_ms,
                    created_at
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            result = cur.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'error': 'No predictions available yet'}), 404
        
        response = {
            'timestamp': result[0].isoformat(),
            'predictions': {
                'tss_mg_l': float(result[1]),
                'cod_mg_l': float(result[2]),
                'bod_mg_l': float(result[3])
            },
            'metadata': {
                'inference_time_ms': float(result[4]),
                'created_at': result[5].isoformat()
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching latest prediction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/predictions/history', methods=['GET'])
def get_prediction_history():
    """Get historical predictions"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 100)), 1000)
        hours = int(request.args.get('hours', 24))
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    timestamp,
                    tss_mg_l,
                    cod_mg_l,
                    bod_mg_l,
                    inference_time_ms
                FROM predictions
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
                LIMIT %s
            """, (hours, limit))
            results = cur.fetchall()
        conn.close()
        
        predictions = []
        for row in results:
            predictions.append({
                'timestamp': row[0].isoformat(),
                'tss_mg_l': float(row[1]),
                'cod_mg_l': float(row[2]),
                'bod_mg_l': float(row[3]),
                'inference_time_ms': float(row[4])
            })
        
        response = {
            'count': len(predictions),
            'predictions': predictions
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/statistics', methods=['GET'])
def get_statistics():
    """Get prediction statistics"""
    try:
        hours = int(request.args.get('hours', 24))
        
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as count,
                    AVG(tss_mg_l) as avg_tss,
                    AVG(cod_mg_l) as avg_cod,
                    AVG(bod_mg_l) as avg_bod,
                    AVG(inference_time_ms) as avg_inference_time,
                    MIN(timestamp) as first_prediction,
                    MAX(timestamp) as last_prediction
                FROM predictions
                WHERE timestamp > NOW() - INTERVAL '%s hours'
            """, (hours,))
            result = cur.fetchone()
        conn.close()
        
        if result[0] == 0:
            return jsonify({'error': 'No predictions in specified time range'}), 404
        
        response = {
            'time_range_hours': hours,
            'total_predictions': int(result[0]),
            'averages': {
                'tss_mg_l': round(float(result[1]), 2) if result[1] else None,
                'cod_mg_l': round(float(result[2]), 2) if result[2] else None,
                'bod_mg_l': round(float(result[3]), 2) if result[3] else None
            },
            'performance': {
                'avg_inference_time_ms': round(float(result[4]), 2) if result[4] else None
            },
            'first_prediction': result[5].isoformat() if result[5] else None,
            'last_prediction': result[6].isoformat() if result[6] else None
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/predictions/batch', methods=['POST'])
def create_batch_prediction():
    """
    Create prediction from batch sensor data
    (For testing/validation purposes)
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['turbidity', 'flow_rate', 'ph', 'dissolved_oxygen', 'temperature', 'aeration_vfd_speed']
        
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
        
        # This would call the prediction service
        # For now, return a placeholder response
        response = {
            'message': 'Batch prediction endpoint - integrate with prediction service',
            'received_data': data
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Wastewater Prediction API...")
    logger.info(f"Database: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    # Wait for database to be ready
    import time
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            conn.close()
            logger.info("✓ Database connection verified")
            break
        except Exception as e:
            if i == max_retries - 1:
                logger.error("Failed to connect to database")
                raise
            logger.warning(f"Database not ready, retrying ({i+1}/{max_retries})...")
            time.sleep(2)
    
    logger.info("="*70)
    logger.info(f"🚀 API Server starting on http://0.0.0.0:5000")
    logger.info("="*70)
    logger.info("Endpoints:")
    logger.info("  GET  /health")
    logger.info("  GET  /api/v1/predictions/latest")
    logger.info("  GET  /api/v1/predictions/history?limit=100&hours=24")
    logger.info("  GET  /api/v1/statistics?hours=24")
    logger.info("  POST /api/v1/predictions/batch")
    logger.info("="*70)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
