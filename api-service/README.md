# API Service

Low-latency REST API that serves real-time water quality predictions to external systems.

## Purpose

Provides a RESTful interface for wastewater treatment plant control systems to access real-time ML predictions, enabling immediate operational decisions based on predicted effluent quality.

## Endpoints

### Health Check
```
GET /health
```
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "wastewater-api",
  "timestamp": "2025-11-19T12:00:00"
}
```

### Get Latest Prediction
```
GET /api/v1/predictions/latest
```
Returns the most recent prediction.

**Response:**
```json
{
  "timestamp": "2025-11-19T12:00:00",
  "predictions": {
    "tss_mg_l": 8.09,
    "cod_mg_l": 41.17,
    "bod_mg_l": 2.17
  },
  "metadata": {
    "inference_time_ms": 152.32,
    "created_at": "2025-11-19T12:00:00.123"
  }
}
```

### Get Prediction History
```
GET /api/v1/predictions/history?limit=100&hours=24
```
Returns historical predictions.

**Query Parameters:**
- `limit`: Maximum number of predictions (default: 100, max: 1000)
- `hours`: Time range in hours (default: 24)

**Response:**
```json
{
  "count": 42,
  "predictions": [
    {
      "timestamp": "2025-11-19T12:00:00",
      "tss_mg_l": 8.09,
      "cod_mg_l": 41.17,
      "bod_mg_l": 2.17,
      "inference_time_ms": 152.32
    }
  ]
}
```

### Get Statistics
```
GET /api/v1/statistics?hours=24
```
Returns aggregated statistics for a time range.

**Query Parameters:**
- `hours`: Time range in hours (default: 24)

**Response:**
```json
{
  "time_range_hours": 24,
  "total_predictions": 288,
  "averages": {
    "tss_mg_l": 8.45,
    "cod_mg_l": 42.30,
    "bod_mg_l": 2.25
  },
  "performance": {
    "avg_inference_time_ms": 145.67
  },
  "first_prediction": "2025-11-18T12:00:00",
  "last_prediction": "2025-11-19T12:00:00"
}
```

### Create Batch Prediction (Placeholder)
```
POST /api/v1/predictions/batch
```
Endpoint for future batch prediction capabilities.

## Configuration

Environment variables:
- `DB_HOST`: PostgreSQL host (default: postgres)
- `DB_PORT`: PostgreSQL port (default: 5432)
- `DB_NAME`: Database name (default: wastewater)
- `DB_USER`: Database user (default: postgres)
- `DB_PASSWORD`: Database password (default: postgres)

## Server Configuration

- **Framework**: Flask + Gunicorn
- **Port**: 5000
- **Workers**: 2
- **Timeout**: 60 seconds
- **CORS**: Enabled for all origins

## Usage Examples

### cURL
```bash
# Get latest prediction
curl http://localhost:5000/api/v1/predictions/latest

# Get last 50 predictions from past 12 hours
curl "http://localhost:5000/api/v1/predictions/history?limit=50&hours=12"

# Get daily statistics
curl "http://localhost:5000/api/v1/statistics?hours=24"
```

### Python
```python
import requests

# Get latest prediction
response = requests.get('http://localhost:5000/api/v1/predictions/latest')
data = response.json()
print(f"TSS: {data['predictions']['tss_mg_l']} mg/L")
```

### JavaScript
```javascript
// Get latest prediction
fetch('http://localhost:5000/api/v1/predictions/latest')
  .then(response => response.json())
  .then(data => console.log('TSS:', data.predictions.tss_mg_l, 'mg/L'));
```

## Integration with Control Systems

This API is designed to integrate with:
- SCADA systems
- PLC controllers
- HMI interfaces
- Data historians
- Dashboard applications

## Dependencies

- flask - Web framework
- flask-cors - CORS support
- gunicorn - WSGI server
- psycopg2-binary - PostgreSQL client
