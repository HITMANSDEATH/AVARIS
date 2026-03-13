import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

// Convert markdown formatting to HTML
function formatMarkdown(text) {
  if (!text) return '';
  
  return text
    // Bold: **text** -> <strong>text</strong>
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic: *text* -> <em>text</em> (but not bullet points)
    .replace(/(?<!\*)\*(?!\*)(.+?)\*(?!\*)/g, '<em>$1</em>')
    // Line breaks
    .replace(/\n/g, '<br>')
    // Bullet points: * item -> <li>item</li>
    .replace(/^[\*\-] (.+)$/gm, '<li>$1</li>')
    // Wrap consecutive list items in <ul>
    .replace(/(<li>.*?<\/li>)(<br>)?(?=<li>|$)/gs, '$1')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
}

function App() {
  const [sensorData, setSensorData] = useState({ temperature: 0, humidity: 0, dust: 0 });
  const [riskData, setRiskData] = useState({ risk_level: 'UNKNOWN', confidence: 0 });
  const [anomalies, setAnomalies] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCameraPanel, setShowCameraPanel] = useState(false);
  const [foodAnalysisResult, setFoodAnalysisResult] = useState(null);

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

  const handleCameraCapture = (result) => {
    // Update the food analysis result when camera captures
    setFoodAnalysisResult(result);
    // Close camera panel after successful capture
    setShowCameraPanel(false);
  };

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

      {/* AVARIS Cam Button */}
      <div style={{ textAlign: 'center', margin: '1rem 0' }}>
        <button 
          className="btn-primary avaris-cam-btn"
          onClick={() => setShowCameraPanel(!showCameraPanel)}
        >
          📷 AVARIS Cam
        </button>
      </div>

      {/* Camera Panel */}
      {showCameraPanel && (
        <CameraPanel 
          API_BASE={API_BASE} 
          onClose={() => setShowCameraPanel(false)}
          onCapture={handleCameraCapture}
        />
      )}

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

      <FoodAnalysisPanel 
        API_BASE={API_BASE} 
        cameraResult={foodAnalysisResult}
        onResultUpdate={setFoodAnalysisResult}
      />
    </div>
  );
}

function CameraPanel({ API_BASE, onClose, onCapture }) {
  const [cameraAvailable, setCameraAvailable] = useState(true);
  const [capturing, setCapturing] = useState(false);
  const [error, setError] = useState(null);
  const [streamLoaded, setStreamLoaded] = useState(false);
  const [streamPaused, setStreamPaused] = useState(false);
  const imgRef = useRef(null);
  const refreshIntervalRef = useRef(null);

  // Direct ESP32-CAM URLs
  const ESP32_CAM_IP = '192.168.1.40';
  const streamUrl = `http://${ESP32_CAM_IP}/stream`;

  useEffect(() => {
    // Setup keyboard listener for Enter key - only when camera panel is open
    const handleKeyPress = (event) => {
      if (event.key === 'Enter' && !capturing && cameraAvailable && !streamPaused) {
        event.preventDefault();
        captureSequence();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [capturing, cameraAvailable, streamPaused]);

  useEffect(() => {
    // Optimized stream loading - start immediately and refresh periodically
    if (imgRef.current && !streamPaused) {
      // Set initial stream URL
      imgRef.current.src = streamUrl;
      
      // Start refresh interval
      startStreamRefresh();
    }

    return () => stopStreamRefresh();
  }, [streamUrl, streamLoaded, streamPaused]);

  const startStreamRefresh = () => {
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }
    
    refreshIntervalRef.current = setInterval(() => {
      if (imgRef.current && streamLoaded && !streamPaused) {
        const timestamp = new Date().getTime();
        imgRef.current.src = `${streamUrl}?t=${timestamp}`;
      }
    }, 100);
  };

  const stopStreamRefresh = () => {
    if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
      refreshIntervalRef.current = null;
    }
  };

  const pauseStream = () => {
    console.log('🛑 Stopping stream display for capture...');
    setStreamPaused(true);
    stopStreamRefresh();
    
    // Actually stop displaying the stream by clearing the src
    if (imgRef.current) {
      imgRef.current.src = '';  // Clear the stream source
      imgRef.current.style.display = 'none';  // Hide the image element
    }
  };

  const resumeStream = () => {
    console.log('▶️ Restarting stream display after capture...');
    setStreamPaused(false);
    
    if (imgRef.current) {
      imgRef.current.style.display = 'block';  // Show the image element
      // Force refresh with new timestamp to restart stream
      const timestamp = new Date().getTime();
      imgRef.current.src = `${streamUrl}?t=${timestamp}`;
    }
    
    // Restart refresh interval
    startStreamRefresh();
  };

  const captureSequence = async () => {
    console.log('🔥 Enter key pressed - starting capture sequence...');
    setCapturing(true);
    setError(null);

    try {
      // 1️⃣ Pause the stream
      pauseStream();
      
      // Small delay to ensure stream is paused
      await new Promise(resolve => setTimeout(resolve, 200));

      // 2️⃣ Call /capture and 3️⃣ Send to AI pipeline
      console.log('📸 Calling backend capture...');
      const response = await fetch(`${API_BASE}/capture-food-image`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      console.log('✅ Capture and analysis successful:', data);
      
      // Pass result to parent component
      onCapture(data);
      
    } catch (err) {
      console.error('❌ Capture sequence failed:', err);
      setError(`Capture failed: ${err.message}`);
    } finally {
      // 4️⃣ Resume the stream (always, even on error)
      setTimeout(() => {
        resumeStream();
        setCapturing(false);
      }, 500); // Small delay before resuming
    }
  };

  const handleStreamError = () => {
    console.error('❌ Stream error');
    setCameraAvailable(false);
    setStreamLoaded(false);
    setError('ESP32-CAM stream connection lost. Check camera at ' + ESP32_CAM_IP);
  };

  const handleStreamLoad = () => {
    console.log('✅ Stream loaded successfully');
    setCameraAvailable(true);
    setStreamLoaded(true);
    setError(null);
  };

  return (
    <div className="camera-panel-overlay">
      <div className="camera-panel">
        <div className="camera-panel-header">
          <h3>📷 AVARIS Camera Feed</h3>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="camera-content">
          <div className="camera-stream-container">
            <div className="stream-wrapper">
              <img
                ref={imgRef}
                id="avarisCamFeed"
                src={streamUrl}
                width="480"
                height="360"
                alt="AVARIS Camera Feed"
                className="camera-stream"
                onError={handleStreamError}
                onLoad={handleStreamLoad}
                style={{ 
                  opacity: streamLoaded ? 1 : 0.5,
                  transition: 'opacity 0.3s ease',
                  display: streamPaused ? 'none' : 'block'
                }}
              />
              
              {/* Show placeholder when stream is paused */}
              {streamPaused && (
                <div className="stream-placeholder">
                  <div className="placeholder-content">
                    <div className="capture-icon">📸</div>
                    <p>Capturing Image...</p>
                    <div className="capture-progress">
                      <div className="progress-bar"></div>
                    </div>
                  </div>
                </div>
              )}
              
              {!streamLoaded && !streamPaused && (
                <div className="stream-loading">
                  <div className="loading-spinner">🔄</div>
                  <p>Loading camera stream...</p>
                </div>
              )}
              
              <div className="stream-overlay">
                {streamPaused ? (
                  <div className="capture-in-progress">
                    <div className="capturing-indicator">
                      📸 Capturing & Analyzing...
                    </div>
                    <div className="stream-status">
                      Stream stopped
                    </div>
                  </div>
                ) : (
                  <div className="capture-instruction">
                    Press <kbd>Enter</kbd> to capture
                  </div>
                )}
                
                <div className="stream-info">
                  ESP32-CAM: {ESP32_CAM_IP} {streamPaused ? '(Stopped)' : '(Live)'}
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="camera-error">
              ⚠️ {error}
            </div>
          )}

          {!cameraAvailable && (
            <div className="camera-unavailable">
              <p>📷 ESP32-CAM Unavailable</p>
              <small>Check camera connection at {ESP32_CAM_IP}</small>
              <button 
                className="retry-btn" 
                onClick={() => {
                  setCameraAvailable(true);
                  setStreamLoaded(false);
                  setStreamPaused(false);
                  setError(null);
                  if (imgRef.current) {
                    imgRef.current.src = `${streamUrl}?t=${new Date().getTime()}`;
                  }
                }}
              >
                Retry Connection
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function FoodAnalysisPanel({ API_BASE, cameraResult, onResultUpdate }) {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  // Update result when camera captures or component mounts
  useEffect(() => {
    if (cameraResult) {
      setResult(cameraResult);
    } else {
      // Fetch latest analysis on load if no camera result
      const fetchLatest = async () => {
        try {
          const res = await fetch(`${API_BASE}/latest-food-analysis`);
          if (res.ok) {
            const data = await res.json();
            if (data) {
              setResult(data);
              onResultUpdate(data);
            }
          }
        } catch (e) {
          console.error("Error fetching latest food analysis:", e);
        }
      };
      fetchLatest();
    }
  }, [API_BASE, cameraResult, onResultUpdate]);

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
      onResultUpdate(data);
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
                <div 
                  style={{ whiteSpace: 'pre-wrap' }}
                  dangerouslySetInnerHTML={{ 
                    __html: formatMarkdown(result.ai_explanation) 
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default App;