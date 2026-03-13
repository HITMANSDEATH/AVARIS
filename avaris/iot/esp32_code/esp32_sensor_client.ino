/*
 * ESP32 Sensor Server for AVARIS Environmental Monitor
 * Acts as HTTP server exposing sensor data via REST API
 * Backend polls this ESP32 for sensor readings instead of ESP32 pushing data
 * 
 * Hardware Requirements:
 * - ESP32 Development Board
 * - DHT22 (Temperature & Humidity sensor)
 * - GP2Y1010AU0F (Dust sensor) or similar
 * - 220uF capacitor and 150 ohm resistor for dust sensor
 * 
 * Pin Connections:
 * - DHT22: Data pin to GPIO 4
 * - Dust Sensor: LED pin to GPIO 2, Analog out to GPIO 36
 * 
 * Endpoints:
 * - GET /sensors -> Returns latest sensor readings in JSON format
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <DHT.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Web Server Configuration
WebServer server(80);  // HTTP server on port 80

// Sensor Configuration
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define DUST_LED_PIN 2
#define DUST_ANALOG_PIN 36

// Timing Configuration
const unsigned long SENSOR_UPDATE_INTERVAL = 5000;  // Update sensor readings every 5 seconds
const unsigned long WIFI_TIMEOUT = 10000;           // 10 seconds WiFi connection timeout

// Initialize sensors
DHT dht(DHT_PIN, DHT_TYPE);

// Global variables for latest sensor readings
struct SensorData {
  float temperature;
  float humidity;
  float dust;
  unsigned long lastUpdate;
  bool valid;
} latestSensorData = {0, 0, 0, 0, false};

void setup() {
  Serial.begin(115200);
  Serial.println("AVARIS ESP32 Sensor Server Starting...");
  
  // Initialize sensor pins
  pinMode(DUST_LED_PIN, OUTPUT);
  digitalWrite(DUST_LED_PIN, LOW);
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup web server routes
  setupWebServer();
  
  // Start the server
  server.begin();
  Serial.println("HTTP server started");
  Serial.printf("Access sensor data at: http://%s/sensors\n", WiFi.localIP().toString().c_str());
  
  Serial.println("Setup complete. Reading sensors...");
}

void loop() {
  // Handle web server requests
  server.handleClient();
  
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Attempting to reconnect...");
    connectToWiFi();
  }
  
  // Update sensor readings at specified interval
  if (millis() - latestSensorData.lastUpdate >= SENSOR_UPDATE_INTERVAL) {
    updateSensorReadings();
  }
  
  delay(100);  // Small delay to prevent excessive CPU usage
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  unsigned long startTime = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - startTime < WIFI_TIMEOUT) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi connected successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void setupWebServer() {
  // Handle /sensors endpoint
  server.on("/sensors", HTTP_GET, handleSensorsRequest);
  
  // Handle root endpoint for basic info
  server.on("/", HTTP_GET, handleRootRequest);
  
  // Handle 404 errors
  server.onNotFound(handleNotFound);
}

void handleSensorsRequest() {
  Serial.println("Received /sensors request");
  
  // Create JSON response
  StaticJsonDocument<200> doc;
  
  if (latestSensorData.valid) {
    doc["temperature"] = latestSensorData.temperature;
    doc["humidity"] = latestSensorData.humidity;
    doc["dust"] = latestSensorData.dust;
    doc["timestamp"] = latestSensorData.lastUpdate;
    doc["status"] = "ok";
  } else {
    doc["temperature"] = 0;
    doc["humidity"] = 0;
    doc["dust"] = 0;
    doc["timestamp"] = 0;
    doc["status"] = "no_data";
  }
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send response with CORS headers
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
  server.send(200, "application/json", jsonString);
  
  Serial.println("Sent sensor data: " + jsonString);
}

void handleRootRequest() {
  String html = "<html><body>";
  html += "<h1>AVARIS ESP32 Sensor Server</h1>";
  html += "<p>Status: " + String(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected") + "</p>";
  html += "<p>IP: " + WiFi.localIP().toString() + "</p>";
  html += "<p><a href='/sensors'>View Sensor Data (JSON)</a></p>";
  html += "</body></html>";
  
  server.send(200, "text/html", html);
}

void handleNotFound() {
  server.send(404, "text/plain", "Endpoint not found. Available: / and /sensors");
}

void updateSensorReadings() {
  Serial.println("Updating sensor readings...");
  
  // Read temperature and humidity from DHT22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  
  // Read dust level
  float dustDensity = readDustSensor();
  
  // Validate readings
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    latestSensorData.valid = false;
    return;
  }
  
  // Update global sensor data
  latestSensorData.temperature = temperature;
  latestSensorData.humidity = humidity;
  latestSensorData.dust = dustDensity;
  latestSensorData.lastUpdate = millis();
  latestSensorData.valid = true;
  
  // Print readings to serial
  Serial.printf("Updated - Temperature: %.1f°C, Humidity: %.1f%%, Dust: %.1f µg/m³\n", 
                temperature, humidity, dustDensity);
}

float readDustSensor() {
  // GP2Y1010AU0F dust sensor reading
  // This sensor requires precise timing for LED control
  
  float voMeasured = 0;
  float calcVoltage = 0;
  float dustDensity = 0;
  
  // Take multiple samples for accuracy
  const int samples = 10;
  float totalVoltage = 0;
  
  for (int i = 0; i < samples; i++) {
    digitalWrite(DUST_LED_PIN, LOW);  // Turn on LED
    delayMicroseconds(280);           // Wait 0.28ms
    
    voMeasured = analogRead(DUST_ANALOG_PIN);  // Read analog value
    
    delayMicroseconds(40);            // Wait 0.04ms
    digitalWrite(DUST_LED_PIN, HIGH); // Turn off LED
    delayMicroseconds(9680);          // Wait 9.68ms (total cycle = 10ms)
    
    // Convert to voltage (ESP32 ADC: 0-4095 = 0-3.3V)
    calcVoltage = voMeasured * (3.3 / 4095.0);
    totalVoltage += calcVoltage;
    
    delay(10);  // Small delay between samples
  }
  
  // Average the samples
  calcVoltage = totalVoltage / samples;
  
  // Convert voltage to dust density (µg/m³)
  // Formula based on GP2Y1010AU0F datasheet
  if (calcVoltage >= 0.6) {
    dustDensity = (calcVoltage - 0.6) * 500;  // Approximate conversion
  } else {
    dustDensity = 0;
  }
  
  // Limit to reasonable range
  if (dustDensity > 500) dustDensity = 500;
  if (dustDensity < 0) dustDensity = 0;
  
  return dustDensity;
}