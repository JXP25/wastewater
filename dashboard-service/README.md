# Dashboard Service

Real-time web dashboard for monitoring wastewater treatment plant ML predictions and system performance.

## Purpose

Provides a user-friendly visual interface to monitor the entire ML prediction pipeline in real-time. No authentication required - direct access to all system metrics and predictions.

## Features

### 📊 Latest Predictions

- Real-time display of TSS, COD, and BOD predictions
- Color-coded quality indicators (Excellent/Good/Warning/High)
- Inference time tracking
- Last prediction timestamp

### 📈 24-Hour Statistics

- Total predictions count
- Average inference time
- Average water quality parameters
- Speed improvement comparison (vs 48-hour lab tests)

### 📉 Prediction History

- Interactive line charts for all parameters
- Model performance tracking (inference time)
- Recent predictions table (last 10)
- Auto-refreshing every 5 seconds

### 🟢 System Status

- Real-time health monitoring
- Connection status to API service
- Error notifications

## Technology Stack

- **React 18** - UI framework
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **Nginx** - Production web server
- **Docker** - Containerization

## Configuration

### Environment Variables

Set in docker-compose.yml:

- `REACT_APP_API_URL` - API service URL (default: http://localhost:8000)

### API Endpoints Used

- `GET /health` - System health check
- `GET /api/v1/predictions/latest` - Latest prediction
- `GET /api/v1/predictions/history?limit=50` - Historical data
- `GET /api/v1/statistics?hours=24` - Aggregated statistics

## Development

### Run Locally

```bash
# Install dependencies
npm install

# Start development server
npm start

# Open http://localhost:3000
```

### Build for Production

```bash
npm run build
```

## Docker Deployment

Dashboard is served via Nginx on port 3000:

```bash
# Build image
docker build -t wastewater-dashboard .

# Run container
docker run -p 3000:3000 \
  -e REACT_APP_API_URL=http://localhost:8000 \
  wastewater-dashboard
```

## Auto-Refresh

Dashboard automatically refreshes data every 5 seconds to provide near-real-time monitoring without manual page refresh.

## User Interface

### Color Coding

Water quality parameters use color-coded indicators:

**TSS (Total Suspended Solids)**

- 🟢 Excellent: < 10 mg/L
- 🟢 Good: 10-15 mg/L
- 🟠 Warning: 15-20 mg/L
- 🔴 High: > 20 mg/L

**COD (Chemical Oxygen Demand)**

- 🟢 Excellent: < 40 mg/L
- 🟢 Good: 40-50 mg/L
- 🟠 Warning: 50-60 mg/L
- 🔴 High: > 60 mg/L

**BOD (Biochemical Oxygen Demand)**

- 🟢 Excellent: < 3 mg/L
- 🟢 Good: 3-5 mg/L
- 🟠 Warning: 5-8 mg/L
- 🔴 High: > 8 mg/L

## Responsive Design

Dashboard is fully responsive and works on:

- Desktop computers (optimal experience)
- Tablets
- Mobile phones

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Integration

### SCADA Integration

Display dashboard on HMI screens:

```html
<iframe src="http://localhost:3000" width="100%" height="100%"></iframe>
```

### Kiosk Mode

Run dashboard in fullscreen for control room displays:

```bash
# Chrome kiosk mode
google-chrome --kiosk --app=http://localhost:3000
```

## Monitoring Capabilities

1. **Real-Time Prediction Tracking**

   - See predictions as they happen
   - Verify model is processing data
   - Check inference performance

2. **Trend Analysis**

   - Visual charts show parameter trends
   - Identify patterns in water quality
   - Spot anomalies quickly

3. **Performance Monitoring**

   - Track model inference speed
   - Ensure sub-second performance
   - Compare with baseline metrics

4. **System Health**
   - Verify all services are running
   - Check API connectivity
   - Monitor for errors

## Dependencies

- react: ^18.2.0
- react-dom: ^18.2.0
- recharts: ^2.10.3 (charts)
- axios: ^1.6.2 (HTTP)
- react-scripts: 5.0.1 (build tools)
