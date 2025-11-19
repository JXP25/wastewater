import React from 'react';
import './Statistics.css';

const Statistics = ({ data }) => {
  if (!data || !data.averages) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>📈 24-Hour Statistics</h2>
        </div>
        <div className="no-data">No statistics available yet</div>
      </div>
    );
  }

  const { averages, total_predictions, performance } = data;

  const statItems = [
    {
      label: 'Total Predictions',
      value: total_predictions,
      unit: '',
      icon: '🎯',
      color: '#2196f3'
    },
    {
      label: 'Avg Inference Time',
      value: performance?.avg_inference_time_ms?.toFixed(2),
      unit: 'ms',
      icon: '⚡',
      color: '#ff9800'
    },
    {
      label: 'Avg TSS',
      value: averages.tss_mg_l?.toFixed(2),
      unit: 'mg/L',
      icon: '💧',
      color: '#4caf50'
    },
    {
      label: 'Avg COD',
      value: averages.cod_mg_l?.toFixed(2),
      unit: 'mg/L',
      icon: '🧪',
      color: '#9c27b0'
    },
    {
      label: 'Avg BOD',
      value: averages.bod_mg_l?.toFixed(2),
      unit: 'mg/L',
      icon: '🦠',
      color: '#f44336'
    }
  ];

  const speedImprovement = 48 * 60 * 60 * 1000; // 48 hours in ms
  const currentTime = performance?.avg_inference_time_ms || 100;
  const improvement = ((speedImprovement / currentTime) * 100).toFixed(0);

  return (
    <div className="card statistics">
      <div className="card-header">
        <h2>📈 24-Hour Statistics</h2>
      </div>

      <div className="stats-grid">
        {statItems.map((stat, index) => (
          <div key={index} className="stat-item" style={{ borderLeftColor: stat.color }}>
            <div className="stat-icon" style={{ color: stat.color }}>
              {stat.icon}
            </div>
            <div className="stat-content">
              <div className="stat-label">{stat.label}</div>
              <div className="stat-value">
                {stat.value} <span className="stat-unit">{stat.unit}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="improvement-banner">
        <div className="improvement-content">
          <span className="improvement-icon">🚀</span>
          <div>
            <div className="improvement-title">Speed Improvement</div>
            <div className="improvement-value">{improvement}x faster than lab tests</div>
            <div className="improvement-subtitle">
              {currentTime.toFixed(0)}ms vs 48 hours
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Statistics;
