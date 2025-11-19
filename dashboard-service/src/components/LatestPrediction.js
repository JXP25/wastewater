import React from 'react';
import './LatestPrediction.css';

const LatestPrediction = ({ data }) => {
  if (!data || !data.predictions) {
    return (
      <div className="card">
        <div className="card-header">
          <h2>📊 Latest Prediction</h2>
        </div>
        <div className="no-data">No predictions available yet</div>
      </div>
    );
  }

  const { predictions, metadata, timestamp } = data;

  const getQualityIndicator = (value, thresholds) => {
    if (value < thresholds.good) return { status: 'excellent', color: '#4caf50', label: 'Excellent' };
    if (value < thresholds.warning) return { status: 'good', color: '#8bc34a', label: 'Good' };
    if (value < thresholds.danger) return { status: 'warning', color: '#ff9800', label: 'Warning' };
    return { status: 'danger', color: '#f44336', label: 'High' };
  };

  const metrics = [
    {
      name: 'TSS',
      fullName: 'Total Suspended Solids',
      value: predictions.tss_mg_l,
      unit: 'mg/L',
      thresholds: { good: 10, warning: 15, danger: 20 },
      icon: '💧'
    },
    {
      name: 'COD',
      fullName: 'Chemical Oxygen Demand',
      value: predictions.cod_mg_l,
      unit: 'mg/L',
      thresholds: { good: 40, warning: 50, danger: 60 },
      icon: '🧪'
    },
    {
      name: 'BOD',
      fullName: 'Biochemical Oxygen Demand',
      value: predictions.bod_mg_l,
      unit: 'mg/L',
      thresholds: { good: 3, warning: 5, danger: 8 },
      icon: '🦠'
    }
  ];

  return (
    <div className="card latest-prediction">
      <div className="card-header">
        <h2>📊 Latest Prediction</h2>
        <span className="timestamp">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </div>

      <div className="metrics-grid">
        {metrics.map((metric) => {
          const quality = getQualityIndicator(metric.value, metric.thresholds);
          return (
            <div key={metric.name} className="metric-card" style={{ borderLeftColor: quality.color }}>
              <div className="metric-header">
                <span className="metric-icon">{metric.icon}</span>
                <div className="metric-info">
                  <h3>{metric.name}</h3>
                  <p className="metric-full-name">{metric.fullName}</p>
                </div>
              </div>
              <div className="metric-value">
                <span className="value">{metric.value.toFixed(2)}</span>
                <span className="unit">{metric.unit}</span>
              </div>
              <div className="quality-indicator" style={{ backgroundColor: quality.color }}>
                {quality.label}
              </div>
            </div>
          );
        })}
      </div>

      <div className="inference-info">
        <span className="inference-badge">
          ⚡ Inference Time: {metadata?.inference_time_ms?.toFixed(2) || 'N/A'} ms
        </span>
        <span className="inference-badge">
          🤖 Model: LSTM v1
        </span>
      </div>
    </div>
  );
};

export default LatestPrediction;
