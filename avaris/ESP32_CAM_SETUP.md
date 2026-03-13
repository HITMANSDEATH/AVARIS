# ESP32-CAM AVARIS Integration Setup Guide

## Overview
This guide explains how to set up the ESP32-CAM for live streaming and food image capture with the AVARIS system.

## Hardware Requirements
- ESP32-CAM module (AI-Thinker model recommended)
- USB-to-Serial adapter (FTDI or CP2102)
- Jumper wires
- Breadboard (optional)
- 5V power supply (recommended for stable operation)

## ESP32-CAM Wiring

### Programming Mode (Upload Code)
```
ESP32-CAM    USB-Serial Adapter
VCC      ->  5V
GND      ->  GND
U0R      ->  TX
U0T      ->  RX
IO0      ->  GND (for programming mode)
```

### Normal Operation Mode
```
ESP32-CAM    Power Supply
VCC      ->  5V
GND      ->  GND
(Remove IO0 to GND connection)
```

## Software Setup

### 1. Arduino IDE Configuration
1. Install Arduino IDE (version 1.8.19 or later)
2. Add ESP32 board support:
   - Go to File > Preferences
   - Add this URL to "Additional Board Manager URLs":
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
3. Install ESP32 boards:
   - Go to Tools > Board > Boards Manager
   - Search for "ESP32" and install "ESP32 by Espressif Systems"
4. Select board: Tools > Board > ESP32 Arduino > AI Thinker ESP32-CAM

### 2. Upload ESP32-CAM Code
1. Open `avaris/iot/esp32cam_code/esp32cam_avaris.ino`
2. Update WiFi credentials:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Connect ESP32-CAM in programming mode
4. Select correct COM port in Tools > Port
5. Upload the code (may take 2-3 attempts)

### 3. Find ESP32-CAM IP Address
1. Open Serial Monitor (115200 baud)
2. Reset ESP32-CAM (remove IO0-GND connection first)
3. Note the IP address displayed in Serial Monitor
4. Update the IP in your AVARIS configuration

## AVARIS Backend Configuration

### 1. Update Environment Variables
Create or update `.env` file in the `avaris` directory:
```env
ESP32_CAM_IP=192.168.1.100
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Test Camera Connection
```bash
# Test if camera is reachable
curl http://192.168.1.100/status

# Test image capture
curl http://192.168.1.100/capture --output test_image.jpg

# Test LED control
curl http://192.168.1.100/led/on
curl http://192.168.1.100/led/off
```

## Camera Configuration Details

### Stream Settings (Live Preview)
- **Resolution**: QVGA (320x240)
- **Quality**: 12 (moderate compression)
- **Frame Buffer**: 2 buffers for smooth streaming
- **Stream URL**: `http://ESP32_CAM_IP:81/stream`

### Capture Settings (AI Analysis)
- **Resolution**: SVGA (800x600)
- **Quality**: 10 (high quality, low compression)
- **LED Flash**: Enabled (200ms duration)
- **Capture URL**: `http://ESP32_CAM_IP/capture`

## Usage Instructions

### 1. Start AVARIS System
```bash
cd avaris
python main.py
```

### 2. Open Frontend Dashboard
```bash
cd avaris/frontend
npm run dev
```

### 3. Use AVARIS Cam
1. Click "📷 AVARIS Cam" button in dashboard
2. Live stream should appear automatically
3. Press **Enter** key to capture and analyze food
4. View results with allergen detection and AI guidance

## Troubleshooting

### Camera Not Connecting
- Check WiFi credentials in ESP32-CAM code
- Verify ESP32-CAM is powered properly (5V recommended)
- Check IP address in Serial Monitor
- Ensure ESP32-CAM and computer are on same network

### Stream Freezing
- The frontend automatically refreshes stream every 200ms
- Check network stability
- Restart ESP32-CAM if needed

### Poor Image Quality
- Ensure adequate lighting
- LED flash is enabled by default for captures
- Clean camera lens
- Check power supply stability

### Upload Errors
- Verify correct board selection (AI Thinker ESP32-CAM)
- Try different baud rates (115200, 921600)
- Hold BOOT button while uploading if available
- Check wiring connections

## Network Configuration

### Port Usage
- **Port 80**: Main HTTP server (capture, LED control, status)
- **Port 81**: MJPEG stream server
- **Backend API**: Port 8000
- **Frontend**: Port 5173 (Vite dev server)

### Firewall Settings
Ensure these ports are open on your network:
- ESP32-CAM: 80, 81
- AVARIS Backend: 8000
- AVARIS Frontend: 5173

## Performance Optimization

### For Better Streaming
- Use 2.4GHz WiFi (better range than 5GHz)
- Position ESP32-CAM close to router
- Minimize network traffic during use

### For Better Image Quality
- Use external 5V power supply
- Ensure good lighting conditions
- Keep camera lens clean
- Use LED flash for indoor captures

## Security Considerations

### Network Security
- Change default WiFi credentials
- Use WPA2/WPA3 encryption
- Consider setting up isolated IoT network
- Monitor network traffic

### Access Control
- ESP32-CAM has no built-in authentication
- Consider adding network-level access controls
- Monitor for unauthorized access attempts

## Advanced Configuration

### Custom Camera Settings
Modify these values in the Arduino code for different scenarios:

```cpp
// For outdoor use (bright conditions)
s->set_ae_level(s, -1);     // Reduce exposure
s->set_agc_gain(s, 0);      // Lower gain

// For indoor use (low light)
s->set_ae_level(s, 1);      // Increase exposure
s->set_agc_gain(s, 10);     // Higher gain
```

### Multiple Camera Support
To use multiple ESP32-CAMs:
1. Assign different static IP addresses
2. Update backend configuration for multiple cameras
3. Modify frontend to support camera selection

## Maintenance

### Regular Tasks
- Clean camera lens weekly
- Check power connections monthly
- Update firmware as needed
- Monitor network performance

### Backup Configuration
- Save ESP32-CAM code with your WiFi settings
- Document IP address assignments
- Keep spare ESP32-CAM modules for redundancy

## Support

For issues specific to:
- **ESP32-CAM hardware**: Check Espressif documentation
- **Arduino IDE**: Visit Arduino support forums
- **AVARIS integration**: Check project documentation
- **Network issues**: Consult your router manual

## Next Steps

After successful setup:
1. Test food analysis with various food items
2. Calibrate allergen detection for your needs
3. Set up automated monitoring schedules
4. Consider integrating with home automation systems