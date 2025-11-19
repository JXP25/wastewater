import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './PredictionHistory.css';

const PredictionHistory = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="card prediction-history">
        <div className="card-header">
          <h2>📉 Prediction History (Last 50)</h2>
        </div>
        <div className="no-data">No historical data available yet</div>
      </div>
    );
  }

  // Format data for chart (reverse to show oldest to newest)
  const chartData = [...data].reverse().map((item, index) => ({
    index: index + 1,
    time: new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    TSS: parseFloat(item.tss_mg_l.toFixed(2)),
    COD: parseFloat(item.cod_mg_l.toFixed(2)),
    BOD: parseFloat(item.bod_mg_l.toFixed(2)),
    inference: parseFloat(item.inference_time_ms?.toFixed(2) || 0)
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="tooltip-time">{payload[0].payload.time}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value} {entry.name === 'inference' ? 'ms' : 'mg/L'}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card prediction-history">
      <div className="card-header">
        <h2>📉 Prediction History (Last {data.length})</h2>
        <span className="history-info">Real-time updates every 5 seconds</span>
      </div>

      <div className="charts-container">
        <div className="chart-wrapper">
          <h3 className="chart-title">Water Quality Parameters</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#666"
                style={{ fontSize: '0.85rem' }}
              />
              <YAxis 
                stroke="#666"
                style={{ fontSize: '0.85rem' }}
                label={{ value: 'mg/L', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '0.9rem' }}
              />
              <Line 
                type="monotone" 
                dataKey="TSS" 
                stroke="#4caf50" 
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line 
                type="monotone" 
                dataKey="COD" 
                stroke="#2196f3" 
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
              <Line 
                type="monotone" 
                dataKey="BOD" 
                stroke="#ff9800" 
                strokeWidth={2}
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-wrapper">
          <h3 className="chart-title">Model Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="time" 
                stroke="#666"
                style={{ fontSize: '0.85rem' }}
              />
              <YAxis 
                stroke="#666"
                style={{ fontSize: '0.85rem' }}
                label={{ value: 'ms', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: '0.9rem' }}
              />
              <Line 
                type="monotone" 
                dataKey="inference" 
                stroke="#9c27b0" 
                strokeWidth={2}
                name="Inference Time"
                dot={{ r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="recent-predictions">
        <h3>Recent Predictions</h3>
        <div className="predictions-table-wrapper">
          <table className="predictions-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>TSS (mg/L)</th>
                <th>COD (mg/L)</th>
                <th>BOD (mg/L)</th>
                <th>Inference (ms)</th>
              </tr>
            </thead>
            <tbody>
              {data.slice(0, 10).map((item, index) => (
                <tr key={index}>
                  <td>{new Date(item.timestamp).toLocaleTimeString()}</td>
                  <td>{item.tss_mg_l.toFixed(2)}</td>
                  <td>{item.cod_mg_l.toFixed(2)}</td>
                  <td>{item.bod_mg_l.toFixed(2)}</td>
                  <td>{item.inference_time_ms?.toFixed(2) || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PredictionHistory;
