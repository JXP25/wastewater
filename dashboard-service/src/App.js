import React, { useState, useEffect } from 'react';
import './App.css';
import LatestPrediction from './components/LatestPrediction';
import Statistics from './components/Statistics';
import PredictionHistory from './components/PredictionHistory';
import SystemStatus from './components/SystemStatus';
import IoTSensorData from './components/IoTSensorData';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const KAFKA_API_URL = 'http://localhost:5000'; // For now, we'll use polling approach

function App() {
  const [latestPrediction, setLatestPrediction] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [history, setHistory] = useState([]);
  const [systemHealth, setSystemHealth] = useState(null);
  const [iotSensorData, setIoTSensorData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      // Fetch latest prediction
      const predResponse = await fetch(`${API_BASE_URL}/api/v1/predictions/latest`);
      if (predResponse.ok) {
        const predData = await predResponse.json();
        setLatestPrediction(predData);
      }

      // Fetch statistics
      const statsResponse = await fetch(`${API_BASE_URL}/api/v1/statistics?hours=24`);
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData);
      }

      // Fetch history
      const historyResponse = await fetch(`${API_BASE_URL}/api/v1/predictions/history?limit=50`);
      let hasData = false;
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setHistory(historyData.predictions || []);
        hasData = historyData.predictions && historyData.predictions.length > 0;
      }

      // Fetch system health
      const healthResponse = await fetch(`${API_BASE_URL}/health`);
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        setSystemHealth(healthData);
      }

      // Simulate IoT sensor data (since we don't have a direct endpoint yet)
      // In production, this would fetch from Kafka or a dedicated IoT endpoint
      if (hasData) {
        // Generate mock IoT data based on prediction patterns
        const latestTime = new Date();
        setIoTSensorData({
          plant_id: 'WTP-001',
          timestamp: latestTime.toISOString(),
          sensors: {
            turbidity_ntu: 60 + Math.random() * 20,
            flow_rate_m3h: 700 + Math.random() * 100,
            ph: 7.0 + Math.random() * 0.5,
            temperature_c: 18 + Math.random() * 4,
            dissolved_oxygen_mgl: 7 + Math.random() * 2,
            conductivity_uscm: 800 + Math.random() * 100
          },
          control_actions: {
            aeration_vfd_speed_pct: 70 + Math.random() * 10,
            polymer_dosing_rate_lh: 15 + Math.random() * 8,
            ras_pump_speed_pct: 65 + Math.random() * 10,
            was_pump_rate_m3h: 25 + Math.random() * 10
          },
          metadata: {
            device_status: 'online',
            data_quality: 'good',
            hrt_hours: 6.0,
            tank_volume_m3: 4675.0,
            process_stage: 'activated_sludge',
            ml_ready: true
          }
        });
      }

      setError(null);
    } catch (err) {
      setError('Failed to fetch data from API');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchData();

    // Refresh every 5 seconds
    const interval = setInterval(fetchData, 5000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="App">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <div className="header-title">
            <h1>🌊 Wastewater Treatment Plant</h1>
            <p>Real-Time ML Prediction Dashboard</p>
          </div>
          <SystemStatus health={systemHealth} error={error} />
        </div>
      </header>

      <main className="App-main">
        {error && (
          <div className="error-banner">
            <span>⚠️ {error}</span>
          </div>
        )}

        <div className="dashboard-grid">
          <LatestPrediction data={latestPrediction} />
          <Statistics data={statistics} />
        </div>

        <PredictionHistory data={history} />
        <div></div>
        <IoTSensorData data={iotSensorData} />

        
      </main>

      <footer className="App-footer">
        <p>
          System Status: <span className="status-badge">{systemHealth?.status || 'Unknown'}</span>
        </p>
        <p>Last Updated: {new Date().toLocaleTimeString()}</p>
      </footer>
    </div>
  );
}

export default App;
