# AVARIS - AI Environmental Risk Monitor

AVARIS is an intelligent environmental monitoring system that combines IoT sensors, computer vision, and AI to assess indoor air quality and allergen risks.

## Features

- **Real-time Environmental Monitoring**: Temperature, humidity, and dust level tracking
- **ESP32 Sensor Integration**: Wireless sensor data collection with polling architecture
- **Computer Vision**: Food allergen detection using ESP32-CAM
- **AI Risk Assessment**: Gemini-powered environmental and allergen risk analysis
- **Live Dashboard**: React frontend with real-time sensor data and risk predictions

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   - Copy `.env` and update with your settings
   - Set `GEMINI_API_KEY` for AI features
   - Set `ESP32_SENSOR_IP` for your ESP32 sensor device

3. **Start Backend**
   ```bash
   python main.py
   ```

4. **Start Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Documentation

- `QUICK_START.md` - Detailed setup instructions
- `POLLING_SETUP_GUIDE.md` - ESP32 sensor setup
- `ESP32_CAM_SETUP.md` - Camera integration
- `SENSOR_POLLING_ARCHITECTURE.md` - Technical architecture
- `PYTHON_313_COMPATIBILITY.md` - Python 3.13 compatibility notes
- `GEMINI_API_SETUP.md` - AI configuration

## Testing

- `test_sensor_polling.py` - Comprehensive sensor polling test
- `esp32_sensor_simulator.py` - Hardware simulator for development

## Architecture

AVARIS uses a polling architecture where the backend actively requests sensor data from ESP32 devices, ensuring reliable communication and data freshness.