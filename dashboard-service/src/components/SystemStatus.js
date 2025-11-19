import React from 'react';
import './SystemStatus.css';

const SystemStatus = ({ health, error }) => {
  const isHealthy = health && health.status === 'healthy' && !error;

  return (
    <div className={`system-status ${isHealthy ? 'healthy' : 'unhealthy'}`}>
      <div className="status-indicator">
        <span className={`status-dot ${isHealthy ? 'green' : 'red'}`}></span>
        <span className="status-text">
          {isHealthy ? 'System Operational' : 'System Error'}
        </span>
      </div>
      {health && (
        <div className="status-details">
          <span className="status-service">{health.service}</span>
        </div>
      )}
    </div>
  );
};

export default SystemStatus;
