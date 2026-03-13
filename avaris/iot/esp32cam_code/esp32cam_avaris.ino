/*
 * ESP32-CAM AVARIS Integration
 * Optimized for live streaming and high-quality image capture
 * Features:
 * - MJPEG streaming on port 81
 * - High-quality image capture endpoint
 * - LED flash control
 * - Dual frame size configuration
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <WebServer.h>
#include <WiFiClient.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Camera pin definitions for AI-Thinker ESP32-CAM
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// LED Flash pin
#define FLASH_LED_PIN      4

WebServer server(80);
WebServer streamServer(81);

// Camera configuration
camera_config_t config;
bool cameraInitialized = false;

void setup() {
  Serial.begin(115200);
  Serial.println("AVARIS ESP32-CAM Starting...");

  // Initialize LED pin
  pinMode(FLASH_LED_PIN, OUTPUT);
  digitalWrite(FLASH_LED_PIN, LOW);

  // Initialize camera
  initCamera();

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("WiFi connected! IP address: ");
  Serial.println(WiFi.localIP());

  // Setup web server routes
  setupRoutes();

  // Start servers
  server.begin();
  streamServer.begin();
  
  Serial.println("AVARIS ESP32-CAM Ready!");
  Serial.println("Stream URL: http://" + WiFi.localIP().toString() + ":81/stream");
  Serial.println("Capture URL: http://" + WiFi.localIP().toString() + "/capture");
}

void loop() {
  server.handleClient();
  streamServer.handleClient();
}

void initCamera() {
  // Camera configuration for optimal streaming and capture
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Frame size and quality settings
  // For streaming: QVGA (320x240) with moderate quality
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  cameraInitialized = true;
  Serial.println("Camera initialized successfully");

  // Get camera sensor
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    // Optimize settings for better image quality
    s->set_brightness(s, 0);     // -2 to 2
    s->set_contrast(s, 0);       // -2 to 2
    s->set_saturation(s, 0);     // -2 to 2
    s->set_special_effect(s, 0); // 0 to 6 (0-No Effect, 1-Negative, 2-Grayscale, 3-Red Tint, 4-Green Tint, 5-Blue Tint, 6-Sepia)
    s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    s->set_aec2(s, 0);           // 0 = disable , 1 = enable
    s->set_ae_level(s, 0);       // -2 to 2
    s->set_aec_value(s, 300);    // 0 to 1200
    s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
    s->set_agc_gain(s, 0);       // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
    s->set_bpc(s, 0);            // 0 = disable , 1 = enable
    s->set_wpc(s, 1);            // 0 = disable , 1 = enable
    s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
    s->set_lenc(s, 1);           // 0 = disable , 1 = enable
    s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
    s->set_vflip(s, 0);          // 0 = disable , 1 = enable
    s->set_dcw(s, 1);            // 0 = disable , 1 = enable
    s->set_colorbar(s, 0);       // 0 = disable , 1 = enable
  }
}

void setupRoutes() {
  // Main capture endpoint for high-quality images
  server.on("/capture", HTTP_GET, handleCapture);
  
  // LED control endpoints
  server.on("/led/on", HTTP_GET, handleLedOn);
  server.on("/led/off", HTTP_GET, handleLedOff);
  
  // Status endpoint
  server.on("/status", HTTP_GET, handleStatus);
  
  // MJPEG stream endpoint
  streamServer.on("/stream", HTTP_GET, handleStream);
  
  // CORS headers for all responses
  server.enableCORS(true);
  streamServer.enableCORS(true);
}

void handleCapture() {
  if (!cameraInitialized) {
    server.send(500, "text/plain", "Camera not initialized");
    return;
  }

  // Switch to high-quality capture mode
  sensor_t * s = esp_camera_sensor_get();
  if (s != NULL) {
    s->set_framesize(s, FRAMESIZE_SVGA);  // 800x600 for AI analysis
    s->set_quality(s, 10);                // High quality (lower number = better quality)
  }

  // Small delay to allow settings to take effect
  delay(100);

  // Capture frame
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }

  // Send image
  server.sendHeader("Content-Type", "image/jpeg");
  server.sendHeader("Content-Length", String(fb->len));
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.send_P(200, "image/jpeg", (const char *)fb->buf, fb->len);

  // Return frame buffer
  esp_camera_fb_return(fb);

  // Switch back to streaming mode
  if (s != NULL) {
    s->set_framesize(s, FRAMESIZE_QVGA);  // Back to streaming resolution
    s->set_quality(s, 12);                // Back to streaming quality
  }

  Serial.println("High-quality image captured and sent");
}

void handleStream() {
  WiFiClient client = streamServer.client();
  
  if (!client) {
    return;
  }

  // Send MJPEG headers
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  client.println("Access-Control-Allow-Origin: *");
  client.println();

  while (client.connected()) {
    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Camera capture failed");
      break;
    }

    // Send frame boundary
    client.println("--frame");
    client.println("Content-Type: image/jpeg");
    client.printf("Content-Length: %u\r\n\r\n", fb->len);
    
    // Send image data
    client.write(fb->buf, fb->len);
    client.println();

    esp_camera_fb_return(fb);

    // Small delay for smooth streaming
    delay(50);
  }

  client.stop();
}

void handleLedOn() {
  digitalWrite(FLASH_LED_PIN, HIGH);
  server.send(200, "text/plain", "LED ON");
  Serial.println("LED turned ON");
}

void handleLedOff() {
  digitalWrite(FLASH_LED_PIN, LOW);
  server.send(200, "text/plain", "LED OFF");
  Serial.println("LED turned OFF");
}

void handleStatus() {
  String status = "{";
  status += "\"camera_initialized\":" + String(cameraInitialized ? "true" : "false") + ",";
  status += "\"wifi_connected\":" + String(WiFi.status() == WL_CONNECTED ? "true" : "false") + ",";
  status += "\"ip_address\":\"" + WiFi.localIP().toString() + "\",";
  status += "\"stream_url\":\"http://" + WiFi.localIP().toString() + ":81/stream\",";
  status += "\"capture_url\":\"http://" + WiFi.localIP().toString() + "/capture\"";
  status += "}";
  
  server.send(200, "application/json", status);
}