import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [sensorData, setSensorData] = useState({ temperature: 0, humidity: 0, dust: 0 });
  const [riskData, setRiskData] = useState({ risk_level: 'UNKNOWN', confidence: 0 });
  const [anomalies, setAnomalies] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [sensorRes, riskRes, anomalyRes, forecastRes] = await Promise.allSettled([
        fetch(`${API_BASE}/latest-sensor-data`),
        fetch(`${API_BASE}/risk-prediction`),
        fetch(`${API_BASE}/anomaly-events?limit=5`),
        fetch(`${API_BASE}/forecast`)
      ]);

      if (sensorRes.status === 'fulfilled' && sensorRes.value.ok) {
        setSensorData(await sensorRes.value.json());
      }
      if (riskRes.status === 'fulfilled' && riskRes.value.ok) {
        setRiskData(await riskRes.value.json());
      }
      if (anomalyRes.status === 'fulfilled' && anomalyRes.value.ok) {
        setAnomalies(await anomalyRes.value.json());
      }
      if (forecastRes.status === 'fulfilled' && forecastRes.value.ok) {
        const data = await forecastRes.value.json();
        // Backend returns {"error": "..."} if not enough data
        if (!data.error) setForecast(data);
      }
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Polling every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="app-container" style={{ justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <h2 className="pulse-icon" style={{ color: 'var(--primary)' }}>INITIALIZING AVARIS CORE...</h2>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="header">
        <div>
          <h1>AVARIS</h1>
          <p>AI Environmental Risk Monitor</p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ margin: 0 }}>System Status: <strong style={{ color: 'var(--primary)' }}>ONLINE</strong></p>
          <small style={{ color: 'var(--text-muted)' }}>Auto-sync active</small>
        </div>
      </header>

      <main className="dashboard-grid">
        {/* Sensor Readings */}
        <div className="sensors-container">
          <div className="card">
            <div className="card-title">Temperature</div>
            <div className="sensor-value">
              {sensorData.temperature.toFixed(1)}<span className="sensor-unit">°C</span>
            </div>
          </div>
          <div className="card">
            <div className="card-title">Humidity</div>
            <div className="sensor-value">
              {sensorData.humidity.toFixed(1)}<span className="sensor-unit">%</span>
            </div>
          </div>
          <div className="card">
            <div className="card-title">Dust Level</div>
            <div className="sensor-value">
              {sensorData.dust.toFixed(1)}<span className="sensor-unit">µg/³</span>
            </div>
          </div>
        </div>

        {/* Risk Prediction */}
        <div className="card risk-container">
          <div className="card-title">Current Risk Assessment</div>
          <div className="risk-level-display">
            <div className={`risk-badge risk-${riskData.risk_level}`}>
              {riskData.risk_level}
            </div>
            <p style={{ color: 'var(--text-muted)' }}>
              Confidence: {(riskData.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>

        {/* Forecast Table */}
        <div className="card forecast-container">
          <div className="card-title">AI Forecast (T+30 Mins)</div>
          {forecast ? (
            <table className="forecast-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Current</th>
                  <th>Predicted</th>
                  <th>Trend</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Temperature</td>
                  <td>{sensorData.temperature.toFixed(1)}°C</td>
                  <td style={{ color: 'var(--primary)' }}>{forecast.predicted_temperature.toFixed(1)}°C</td>
                  <td>{forecast.predicted_temperature > sensorData.temperature ? '↗️' : '↘️'}</td>
                </tr>
                <tr>
                  <td>Humidity</td>
                  <td>{sensorData.humidity.toFixed(1)}%</td>
                  <td style={{ color: 'var(--primary)' }}>{forecast.predicted_humidity.toFixed(1)}%</td>
                  <td>{forecast.predicted_humidity > sensorData.humidity ? '↗️' : '↘️'}</td>
                </tr>
                <tr>
                  <td>Dust Level</td>
                  <td>{sensorData.dust.toFixed(1)}µg/³</td>
                  <td style={{ color: 'var(--primary)' }}>{forecast.predicted_dust.toFixed(1)}µg/³</td>
                  <td>{forecast.predicted_dust > sensorData.dust ? '↗️' : '↘️'}</td>
                </tr>
              </tbody>
            </table>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>Insufficient data to generate forecast.</p>
          )}
        </div>

        {/* Anomaly Log */}
        <div className="card anomaly-container">
          <div className="card-title" style={{ color: 'var(--danger)' }}>System Alerts &amp; Anomalies</div>
          <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            {anomalies.length > 0 ? anomalies.map((anomaly, idx) => (
              <div key={idx} className="anomaly-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <strong style={{ color: 'var(--danger)', textTransform: 'uppercase' }}>{anomaly.status}</strong>
                  <small style={{ color: 'var(--text-muted)' }}>
                    {new Date(anomaly.timestamp).toLocaleTimeString()}
                  </small>
                </div>
                <p style={{ fontSize: '0.9rem', marginBottom: '0.5rem', whiteSpace: 'pre-wrap' }}>
                  {anomaly.description}
                </p>
                {anomaly.action && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--warning)', marginTop: '0.5rem' }}>
                    <strong>Action:</strong> {anomaly.action}
                  </div>
                )}
              </div>
            )) : (
              <p style={{ color: 'var(--text-muted)' }}>No recent anomalies detected. System operating normally.</p>
            )}
          </div>
        </div>
      </main>

      <FoodAnalysisPanel API_BASE={API_BASE} />
    </div>
  );
}

function FoodAnalysisPanel({ API_BASE }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch latest analysis on load
    const fetchLatest = async () => {
      try {
        const res = await fetch(`${API_BASE}/latest-food-analysis`);
        if (res.ok) {
          const data = await res.json();
          if (data) setResult(data);
        }
      } catch (e) {
        console.error("Error fetching latest food analysis:", e);
      }
    };
    fetchLatest();
  }, [API_BASE]);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch(`${API_BASE}/upload-food-image`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      setResult(data);
      setFile(null);
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <section className="card food-analysis-panel" style={{ marginTop: '2rem' }}>
      <div className="card-title">Food Allergen Detection</div>
      
      <div className="food-upload-section">
        <input type="file" accept="image/*" onChange={handleFileChange} id="food-upload-input" style={{ display: 'none' }} />
        <label htmlFor="food-upload-input" className="upload-label">
          {file ? file.name : "Select Food Image"}
        </label>
        <button onClick={handleUpload} disabled={uploading || !file} className="btn-primary">
          {uploading ? "Analyzing..." : "Analyze Image"}
        </button>
      </div>

      {error && <p style={{ color: 'var(--danger)', marginTop: '1rem' }}>{error}</p>}

      {result && (
        <div className="food-result-container">
          <div className="food-result-header">
            <h3>{result.food_item}</h3>
            <div className={`risk-badge risk-${result.risk_level}`}>
              {result.risk_level} RISK
            </div>
          </div>

          <div className="food-result-content">
            <div className="food-image-preview">
              <img src={`http://localhost:8000${result.image_url || '/' + result.image_path}`} alt="Analyzed Food" />
            </div>
            
            <div className="food-details">
              <div>
                <strong>Ingredients:</strong>
                <ul className="ingredient-list">
                  {result.ingredients.map((ing, i) => (
                    <li key={i}>{ing}</li>
                  ))}
                </ul>
              </div>

              {result.detected_allergens.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <strong style={{ color: 'var(--danger)' }}>Detected Allergens:</strong>
                  <div className="allergen-tags">
                    {result.detected_allergens.map((alg, i) => (
                      <span key={i} className="allergen-tag">{alg}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="ai-explanation-box" style={{ marginTop: '1.5rem' }}>
                <strong>AI Safety Guidance:</strong>
                <p>{result.ai_explanation}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default App;
