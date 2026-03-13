# AVARIS Sensor Polling Setup Guide

## Quick Setup Steps

### 1. Python Version Compatibility
AVARIS works with Python 3.8+ including Python 3.13. If you encounter `cgi` module errors with Python 3.13, the compatibility fix is already included in the codebase.

### 2. Update ESP32 Firmware
1. Open `avaris/iot/esp32_code/esp32_sensor_client.ino` in Arduino IDE
2. Update WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Upload to ESP32
4. Note the IP address shown in Serial Monitor

### 3. Configure Backend
1. Update `avaris/.env`:
   ```bash
   ESP32_SENSOR_IP="192.168.1.40"  # Use your ESP32's IP
   SENSOR_POLL_INTERVAL="5"        # Poll every 5 seconds
   ```

### 4. Install Dependencies
```bash
cd avaris
pip install -r requirements.txt
```

### 5. Start Backend
```bash
cd avaris
python main.py
```

### 6. Test Setup
```bash
# Test ESP32 directly
curl http://192.168.1.40/sensors

# Test backend polling
curl http://localhost:8000/api/latest-sensors

# Run comprehensive test
python test_sensor_polling.py
```

## Development with Simulator

For development without ESP32 hardware:

1. Start simulator:
   ```bash
   python esp32_sensor_simulator.py
   ```

2. Update .env to use simulator:
   ```bash
   ESP32_SENSOR_IP="localhost:8080"
   ```

3. Start backend and test normally

## Verification Checklist

- [ ] ESP32 shows WiFi connected in Serial Monitor
- [ ] ESP32 IP accessible in browser: `http://ESP32_IP/sensors`
- [ ] Backend starts without errors
- [ ] Backend logs show "ESP32 sensor polling service started"
- [ ] `/api/latest-sensors` returns fresh data
- [ ] Frontend displays live sensor values

## Common Issues

### ESP32 Won't Connect to WiFi
- Double-check SSID and password
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check WiFi signal strength

### Backend Can't Reach ESP32
- Verify ESP32 IP address
- Check firewall settings
- Ensure devices on same network

### Data Shows as Stale
- ESP32 may have crashed or disconnected
- Check ESP32 power supply
- Restart ESP32 if needed

## Next Steps

Once polling is working:
1. Frontend will automatically display live sensor data
2. Risk assessment runs automatically on polled data
3. Historical data is stored for analysis
4. Environment analysis uses latest polled values