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
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showCameraPanel, setShowCameraPanel] = useState(false);
  const [foodAnalysisResult, setFoodAnalysisResult] = useState(null);

  const fetchData = async () => {
    try {
      const [sensorRes, riskRes, forecastRes] = await Promise.allSettled([
        fetch(`${API_BASE}/latest-sensors`),  // Updated to use new polling endpoint
        fetch(`${API_BASE}/risk-prediction`),
        fetch(`${API_BASE}/forecast`)
      ]);

      if (sensorRes.status === 'fulfilled' && sensorRes.value.ok) {
        setSensorData(await sensorRes.value.json());
      }
      if (riskRes.status === 'fulfilled' && riskRes.value.ok) {
        setRiskData(await riskRes.value.json());
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
    console.log('📋 Camera capture result received:', result);
    // Update the food analysis result when camera captures
    setFoodAnalysisResult(result);
    // Close camera panel after successful capture
    setShowCameraPanel(false);
    console.log('📷 Camera panel closed');
    
    // Scroll to food analysis panel after a short delay
    setTimeout(() => {
      console.log('🔍 Attempting to scroll to analysis panel...');
      const analysisPanel = document.querySelector('.food-analysis-panel');
      if (analysisPanel) {
        console.log('✅ Found analysis panel, scrolling...');
        analysisPanel.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      } else {
        console.log('❌ Analysis panel not found');
      }
    }, 1200); // Wait for camera panel to close
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

      {/* Environment Analysis Panel */}
      <EnvironmentAnalysisPanel API_BASE={API_BASE} />

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
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState('');
  const [error, setError] = useState(null);
  const [streamLoaded, setStreamLoaded] = useState(false);
  const [streamPaused, setStreamPaused] = useState(false);
  const imgRef = useRef(null);

  // Direct ESP32-CAM URLs
  const ESP32_CAM_IP = '192.168.1.40';
  const streamUrl = `http://${ESP32_CAM_IP}/stream`;

  useEffect(() => {
    // Setup keyboard listener for Enter key - only when camera panel is open
    const handleKeyPress = (event) => {
      if (event.key === 'Enter' && !capturing && !analyzing && cameraAvailable && streamLoaded && !streamPaused) {
        event.preventDefault();
        captureSequence();
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [capturing, analyzing, cameraAvailable, streamLoaded, streamPaused]);

  useEffect(() => {
    // Load stream when component mounts
    if (imgRef.current && !streamPaused) {
      imgRef.current.src = streamUrl;
    }
  }, [streamUrl, streamPaused]);

  const pauseStream = () => {
    console.log('🛑 Pausing stream for capture...');
    setStreamPaused(true);
    
    if (imgRef.current) {
      // Stop the stream by clearing the src
      imgRef.current.src = '';
    }
  };

  const resumeStream = () => {
    console.log('▶️ Resuming stream after capture...');
    setStreamPaused(false);
    
    if (imgRef.current) {
      // Restart stream with timestamp to force refresh
      const timestamp = new Date().getTime();
      imgRef.current.src = `${streamUrl}?t=${timestamp}`;
    }
  };

  const captureSequence = async () => {
    console.log('🔥 Enter key pressed - starting capture sequence...');
    setCapturing(true);
    setAnalyzing(false);
    setAnalysisStage('');
    setError(null);

    try {
      // 1️⃣ Pause the stream to free up ESP32 resources
      pauseStream();
      setAnalysisStage('Pausing stream...');
      console.log('📊 Stage: Pausing stream...');
      
      // 2️⃣ Wait a moment for stream to fully stop
      await new Promise(resolve => setTimeout(resolve, 500));

      // 3️⃣ Start capture phase
      setAnalysisStage('Capturing image...');
      console.log('📊 Stage: Capturing image...');
      console.log('📸 Calling backend for ESP32 capture...');
      
      // 4️⃣ Switch to analysis phase before making the request
      setCapturing(false);
      setAnalyzing(true);
      setAnalysisStage('Processing image...');
      console.log('📊 Stage: Processing image... (analyzing=true)');

      // 5️⃣ Start the backend request
      const responsePromise = fetch(`${API_BASE}/capture-food-image`, {
        method: 'POST',
      });

      // 6️⃣ Show analysis stages while waiting for response
      const showAnalysisStages = async () => {
        await new Promise(resolve => setTimeout(resolve, 800));
        setAnalysisStage('Analyzing with Gemini AI...');
        console.log('📊 Stage: Analyzing with Gemini AI...');
        
        await new Promise(resolve => setTimeout(resolve, 1200));
        setAnalysisStage('Detecting ingredients...');
        console.log('📊 Stage: Detecting ingredients...');
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        setAnalysisStage('Checking allergens...');
        console.log('📊 Stage: Checking allergens...');
        
        await new Promise(resolve => setTimeout(resolve, 800));
        setAnalysisStage('Generating report...');
        console.log('📊 Stage: Generating report...');
      };

      // Run both the API call and visual stages in parallel
      const [response] = await Promise.all([
        responsePromise,
        showAnalysisStages()
      ]);

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      console.log('✅ Capture and analysis successful:', data);
      
      setAnalysisStage('Analysis complete!');
      console.log('📊 Stage: Analysis complete!');
      
      // 7️⃣ Pass result to parent component
      onCapture(data);
      
      // 8️⃣ Close camera panel after successful analysis
      setTimeout(() => {
        console.log('🔄 Closing camera panel...');
        onClose();
      }, 1500);
      
    } catch (err) {
      console.error('❌ Capture sequence failed:', err);
      setError(`Capture failed: ${err.message}`);
      
      // Resume stream on error
      setTimeout(() => {
        resumeStream();
        setCapturing(false);
        setAnalyzing(false);
        setAnalysisStage('');
      }, 1000);
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

  const isProcessing = capturing || analyzing;

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
              {/* Live stream */}
              <img
                ref={imgRef}
                id="avarisCamFeed"
                src={streamUrl}
                width="480"
                height="360"
                alt="AVARIS Camera Feed"
                className={`camera-stream ${isProcessing ? 'processing' : ''}`}
                onError={handleStreamError}
                onLoad={handleStreamLoad}
                style={{ 
                  opacity: streamLoaded && !streamPaused ? 1 : 0.5,
                  transition: 'opacity 0.3s ease',
                  display: streamPaused || analyzing ? 'none' : 'block'
                }}
              />
              
              {/* Show placeholder when stream is paused or analyzing */}
              {(streamPaused || analyzing) && (
                <div className="stream-placeholder">
                  <div className="placeholder-content">
                    <div className={`capture-icon ${analyzing ? 'analyzing' : ''}`}>
                      {capturing ? '📸' : analyzing ? '🧠' : '📸'}
                    </div>
                    <p>{analysisStage || 'Processing...'}</p>
                    <div className="capture-progress">
                      <div className={`progress-bar ${analyzing ? 'analyzing' : ''}`}></div>
                    </div>
                    {analyzing && (
                      <div className="analysis-details">
                        <div className="analysis-steps">
                          <div className="step active">🔍 Image Analysis</div>
                          <div className="step active">🥗 Ingredient Detection</div>
                          <div className="step active">⚠️ Allergen Check</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {!streamLoaded && !streamPaused && !analyzing && (
                <div className="stream-loading">
                  <div className="loading-spinner">🔄</div>
                  <p>Loading camera stream...</p>
                </div>
              )}
              
              <div className="stream-overlay">
                {isProcessing ? (
                  <div className="capture-in-progress">
                    <div className="capturing-indicator">
                      {capturing ? '📸 Capturing...' : '🧠 Analyzing...'}
                    </div>
                    <div className="stream-status">
                      {analysisStage || (capturing ? 'Stream paused' : 'Processing')}
                    </div>
                  </div>
                ) : (
                  <div className="capture-instruction">
                    Press <kbd>Enter</kbd> to capture
                  </div>
                )}
                
                <div className="stream-info">
                  ESP32-CAM: {ESP32_CAM_IP} {
                    capturing ? '(Capturing)' : 
                    analyzing ? '(Analyzing)' : 
                    streamPaused ? '(Paused)' : '(Live)'
                  }
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
                  setCapturing(false);
                  setAnalyzing(false);
                  setAnalysisStage('');
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

function EnvironmentAnalysisPanel({ API_BASE }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const response = await fetch(`${API_BASE}/analyze-environment`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(`Analysis failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card environment-analysis-panel" style={{ marginTop: '2rem' }}>
      <div className="card-title">🌍 Environment Analysis</div>
      
      <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
        <button 
          className="btn-primary"
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            background: loading ? 'var(--text-muted)' : 'linear-gradient(45deg, var(--primary), #00aaff)',
            color: 'white',
            border: 'none',
            padding: '1rem 2rem',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            borderRadius: '25px',
            cursor: loading ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease',
            textTransform: 'uppercase',
            letterSpacing: '1px'
          }}
        >
          {loading ? '🧠 Analyzing...' : '🔍 Analyze Environment'}
        </button>
      </div>

      {error && (
        <div style={{ 
          color: 'var(--danger)', 
          background: 'rgba(255, 68, 68, 0.1)',
          padding: '1rem',
          borderRadius: '8px',
          border: '1px solid var(--danger)',
          marginBottom: '1rem'
        }}>
          ⚠️ {error}
        </div>
      )}

      {analysis && (
        <div className="environment-analysis-result">
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 2fr', 
            gap: '2rem',
            alignItems: 'start'
          }}>
            {/* Current Readings */}
            <div>
              <h4 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>Current Readings</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                <div style={{ 
                  background: 'rgba(0, 255, 204, 0.1)', 
                  padding: '0.8rem', 
                  borderRadius: '8px',
                  border: '1px solid rgba(0, 255, 204, 0.3)'
                }}>
                  <strong>Temperature:</strong> {analysis.sensor_data.temperature.toFixed(1)}°C
                </div>
                <div style={{ 
                  background: 'rgba(0, 255, 204, 0.1)', 
                  padding: '0.8rem', 
                  borderRadius: '8px',
                  border: '1px solid rgba(0, 255, 204, 0.3)'
                }}>
                  <strong>Humidity:</strong> {analysis.sensor_data.humidity.toFixed(1)}%
                </div>
                <div style={{ 
                  background: 'rgba(0, 255, 204, 0.1)', 
                  padding: '0.8rem', 
                  borderRadius: '8px',
                  border: '1px solid rgba(0, 255, 204, 0.3)'
                }}>
                  <strong>Dust Level:</strong> {analysis.sensor_data.dust.toFixed(1)}µg/m³
                </div>
                <div style={{ 
                  background: analysis.risk_level === 'HIGH' || analysis.risk_level === 'CRITICAL' 
                    ? 'rgba(255, 68, 68, 0.1)' 
                    : analysis.risk_level === 'MEDIUM' 
                    ? 'rgba(255, 170, 0, 0.1)' 
                    : 'rgba(0, 204, 102, 0.1)', 
                  padding: '0.8rem', 
                  borderRadius: '8px',
                  border: `1px solid ${
                    analysis.risk_level === 'HIGH' || analysis.risk_level === 'CRITICAL' 
                      ? 'var(--danger)' 
                      : analysis.risk_level === 'MEDIUM' 
                      ? 'var(--warning)' 
                      : 'var(--success)'
                  }`
                }}>
                  <strong>Risk Level:</strong> {analysis.risk_level}
                </div>
              </div>
              <div style={{ 
                fontSize: '0.8rem', 
                color: 'var(--text-muted)', 
                marginTop: '1rem',
                textAlign: 'center'
              }}>
                Analyzed at: {new Date(analysis.generated_at).toLocaleTimeString()}
              </div>
            </div>

            {/* AI Analysis */}
            <div>
              <h4 style={{ color: 'var(--primary)', marginBottom: '1rem' }}>🤖 AI Analysis</h4>
              <div className="ai-explanation-box" style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '1.5rem',
                fontSize: '1rem',
                lineHeight: '1.6',
                minHeight: '200px'
              }}>
                <div 
                  style={{ whiteSpace: 'pre-wrap' }}
                  dangerouslySetInnerHTML={{ 
                    __html: formatMarkdown(analysis.analysis) 
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