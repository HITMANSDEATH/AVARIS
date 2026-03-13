# AVARIS Sensor Polling Architecture

## Overview

AVARIS now uses a **polling architecture** for ESP32 sensor data instead of the previous push-based approach. This provides more reliable communication and better control over data flow.

## Architecture Components

### 1. ESP32 Sensor Server
- **Role**: Acts as HTTP server exposing sensor data
- **Endpoint**: `GET /sensors`
- **Response**: JSON with temperature, humidity, and dust readings
- **Update Frequency**: Sensors read every 5 seconds

### 2. Backend Polling Service
- **Role**: Continuously polls ESP32 for sensor data
- **Frequency**: Every 5 seconds (configurable)
- **Storage**: Automatically stores data in database
- **Risk Assessment**: Calculates risk levels from polled data

### 3. Backend API
- **Endpoint**: `GET /api/latest-sensors`
- **Purpose**: Provides latest sensor data to frontend
- **Data Source**: In-memory cache from polling service

## Data Flow

```
ESP32 Sensors → ESP32 HTTP Server → Backend Poller → Database + Cache → Frontend
     ↓                ↓                    ↓              ↓           ↓
  DHT22 + Dust    /sensors endpoint   Polls every 5s   Stores data  Displays
```

## Configuration

### ESP32 Configuration
```cpp
// WiFi settings in ESP32 code
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### Backend Configuration (.env)
```bash
ESP32_SENSOR_IP="192.168.1.40"    # ESP32 sensor server IP
SENSOR_POLL_INTERVAL="5"          # Poll every 5 seconds
```

## API Endpoints

### ESP32 Endpoints
- `GET /` - Basic status page
- `GET /sensors` - Latest sensor readings

### Backend Endpoints
- `GET /api/latest-sensors` - Latest polled sensor data
- `GET /api/sensor-data` - Historical sensor data (database)
- `GET /api/analyze-environment` - AI analysis using polled data

## Benefits of Polling Architecture

1. **Reliability**: Backend controls when data is requested
2. **Network Resilience**: Handles ESP32 disconnections gracefully
3. **Data Freshness**: Always knows when data was last updated
4. **Debugging**: Easy to test ESP32 endpoint independently
5. **Scalability**: Can poll multiple ESP32 devices

## Testing

### Test ESP32 Direct Access
```bash
curl http://192.168.1.40/sensors
```

### Test Backend Polling
```bash
curl http://localhost:8000/api/latest-sensors
```

### Run Test Suite
```bash
python test_sensor_polling.py
```

### Use Simulator for Development
```bash
python esp32_sensor_simulator.py
# Then update ESP32_SENSOR_IP to localhost:8080
```

## Troubleshooting

### ESP32 Not Responding
1. Check ESP32 power and WiFi connection
2. Verify IP address in configuration
3. Test direct access: `http://ESP32_IP/sensors`

### Backend Polling Issues
1. Check ESP32_SENSOR_IP in .env file
2. Verify network connectivity
3. Check backend logs for polling errors

### Stale Data Warnings
- Backend returns 503 if data is older than 30 seconds
- Indicates ESP32 may be offline or unreachable

## Migration from Push Architecture

The old push-based system where ESP32 sent POST requests has been replaced. Key changes:

1. **ESP32**: Now runs HTTP server instead of HTTP client
2. **Backend**: Actively polls instead of passively receiving
3. **Database**: Still stores historical data for analysis
4. **Frontend**: Uses new `/api/latest-sensors` endpoint

## Hardware Requirements

- ESP32 with WiFi capability
- DHT22 temperature/humidity sensor
- GP2Y1010AU0F dust sensor
- Stable power supply
- Reliable WiFi network

## Performance Characteristics

- **Latency**: 5-10 seconds (polling interval + processing)
- **Reliability**: High (backend retries on failures)
- **Resource Usage**: Low (simple HTTP requests)
- **Scalability**: Can handle multiple ESP32 devices