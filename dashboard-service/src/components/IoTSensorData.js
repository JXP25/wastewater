import React from 'react';
import './IoTSensorData.css';

const IoTSensorData = ({ data }) => {
  if (!data) {
    return (
      <div className="card iot-sensors">
        <div className="card-header">
          <h2>🔌 IoT Sensor Data</h2>
        </div>
        <div className="no-data">No sensor data available yet</div>
      </div>
    );
  }

  const { sensors, control_actions, metadata } = data;

  const sensorGroups = [
    {
      title: 'Environmental Sensors',
      icon: '🌡️',
      items: [
        {
          name: 'Turbidity',
          value: sensors?.turbidity_ntu,
          unit: 'NTU',
          icon: '💧',
          color: '#2196f3',
          range: { min: 0, max: 100 }
        },
        {
          name: 'Flow Rate',
          value: sensors?.flow_rate_m3h,
          unit: 'm³/h',
          icon: '🌊',
          color: '#00bcd4',
          range: { min: 0, max: 1000 }
        },
        {
          name: 'pH Level',
          value: sensors?.ph,
          unit: '',
          icon: '⚗️',
          color: '#4caf50',
          range: { min: 0, max: 14 }
        },
        {
          name: 'Temperature',
          value: sensors?.temperature_c,
          unit: '°C',
          icon: '🌡️',
          color: '#ff9800',
          range: { min: 0, max: 50 }
        },
        {
          name: 'Dissolved Oxygen',
          value: sensors?.dissolved_oxygen_mgl,
          unit: 'mg/L',
          icon: '💨',
          color: '#9c27b0',
          range: { min: 0, max: 15 }
        },
        {
          name: 'Conductivity',
          value: sensors?.conductivity_uscm,
          unit: 'µS/cm',
          icon: '⚡',
          color: '#f44336',
          range: { min: 0, max: 2000 }
        }
      ]
    },
    {
      title: 'Control Actions',
      icon: '🎛️',
      items: [
        {
          name: 'Aeration VFD Speed',
          value: control_actions?.aeration_vfd_speed_pct,
          unit: '%',
          icon: '💨',
          color: '#3f51b5',
          range: { min: 0, max: 100 }
        },
        {
          name: 'Polymer Dosing Rate',
          value: control_actions?.polymer_dosing_rate_lh,
          unit: 'L/h',
          icon: '💉',
          color: '#673ab7',
          range: { min: 0, max: 50 }
        },
        {
          name: 'RAS Pump Speed',
          value: control_actions?.ras_pump_speed_pct,
          unit: '%',
          icon: '🔄',
          color: '#009688',
          range: { min: 0, max: 100 }
        },
        {
          name: 'WAS Pump Rate',
          value: control_actions?.was_pump_rate_m3h,
          unit: 'm³/h',
          icon: '⚙️',
          color: '#795548',
          range: { min: 0, max: 100 }
        }
      ]
    }
  ];

  const getProgressPercentage = (value, range) => {
    if (!value) return 0;
    return Math.min(100, Math.max(0, ((value - range.min) / (range.max - range.min)) * 100));
  };

  return (
    <div className="card iot-sensors">
      <div className="card-header">
        <h2>🔌 IoT Sensor Data</h2>
        <div className="plant-info">
          <span className="plant-badge">{data.plant_id || 'WTP-001'}</span>
          {metadata?.device_status && (
            <span className={`status-indicator ${metadata.device_status === 'online' ? 'online' : 'offline'}`}>
              <span className="status-dot"></span>
              {metadata.device_status}
            </span>
          )}
        </div>
      </div>

      {sensorGroups.map((group, groupIndex) => (
        <div key={groupIndex} className="sensor-group">
          <h3 className="group-title">
            <span className="group-icon">{group.icon}</span>
            {group.title}
          </h3>
          
          <div className="sensors-grid">
            {group.items.map((sensor, index) => (
              <div key={index} className="sensor-item">
                <div className="sensor-header">
                  <span className="sensor-icon" style={{ color: sensor.color }}>
                    {sensor.icon}
                  </span>
                  <div className="sensor-info">
                    <div className="sensor-name">{sensor.name}</div>
                    <div className="sensor-value">
                      {sensor.value !== undefined ? sensor.value.toFixed(2) : 'N/A'}
                      <span className="sensor-unit">{sensor.unit}</span>
                    </div>
                  </div>
                </div>
                
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: `${getProgressPercentage(sensor.value, sensor.range)}%`,
                      backgroundColor: sensor.color
                    }}
                  ></div>
                </div>
                
                <div className="range-labels">
                  <span>{sensor.range.min}</span>
                  <span>{sensor.range.max} {sensor.unit}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {metadata && (
        <div className="metadata-section">
          <div className="metadata-grid">
            <div className="metadata-item">
              <span className="metadata-label">🏭 Process Stage</span>
              <span className="metadata-value">{metadata.process_stage?.replace('_', ' ')}</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">⏱️ HRT</span>
              <span className="metadata-value">{metadata.hrt_hours?.toFixed(1)} hours</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">🏊 Tank Volume</span>
              <span className="metadata-value">{metadata.tank_volume_m3?.toFixed(0)} m³</span>
            </div>
            <div className="metadata-item">
              <span className="metadata-label">✅ Data Quality</span>
              <span className={`quality-badge ${metadata.data_quality}`}>
                {metadata.data_quality}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IoTSensorData;
