#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// --- Configuration ---
// Replace with your Network credentials
const char* ssid = "Ganeshgj";
const char* password = "shawn123";

// Replace with your Computer's IP address (find it using 'ipconfig' on Windows)
const char* serverUrl = "http://192.168.1.37:8000/api/sensor-data"; 

#define DHTPIN 4      // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22 // Set to DHT22 if you have that model
DHT dht(DHTPIN, DHTTYPE);

#define DUST_SENSOR_PIN 32 // Analog pin connected to the Dust sensor output
#define DUST_LED_PIN 19     // Digital pin connected to the Dust sensor LED control

// --- Variables ---
float temp = 0, hum = 0, dustDensity = 0;

void setup() {
  Serial.begin(115200);
  delay(100);
  
  dht.begin();
  pinMode(DUST_LED_PIN, OUTPUT);
  digitalWrite(DUST_LED_PIN, HIGH); // Start with LED off (active low logic often)

  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 1. Read DHT Sensor (Temperature & Humidity)
  hum = dht.readHumidity();
  temp = dht.readTemperature();

  // 2. Read Dust Sensor (GP2Y1014AU0F Timing Logic)
  digitalWrite(DUST_LED_PIN, LOW); // Turn ON the LED
  delayMicroseconds(280);
  int rawValue = analogRead(DUST_SENSOR_PIN);
  delayMicroseconds(40);
  digitalWrite(DUST_LED_PIN, HIGH); // Turn OFF the LED
  delayMicroseconds(9680);

  // Convert analog value to voltage and then to dust density
  float voltage = rawValue * (3.3 / 4095.0);
  // Linear formula: density = 0.17 * voltage - 0.1 (approximate, varies by sensor)
  dustDensity = (0.17 * voltage - 0.1) * 1000.0; // mg/m3 to ug/m3
  if (dustDensity < 0) dustDensity = 0;

  if (isnan(hum) || isnan(temp)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Temp: "); Serial.print(temp); Serial.print("°C | ");
    Serial.print("Hum: "); Serial.print(hum); Serial.print("% | ");
    Serial.print("Dust: "); Serial.print(dustDensity); Serial.println(" ug/m3");

    // 3. Send to Backend
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.setTimeout(10000); // Wait up to 10 seconds for a response
      http.addHeader("Content-Type", "application/json");

      // Construct JSON payload
      String jsonPayload = "{\"temperature\": " + String(temp, 2) + 
                           ", \"humidity\": " + String(hum, 1) + 
                           ", \"dust\": " + String(dustDensity, 1) + "}";

      Serial.print("Sending payload: ");
      Serial.println(jsonPayload);

      int httpResponseCode = http.POST(jsonPayload);
      
      if (httpResponseCode > 0) {
        Serial.print("Backend Response: ");
        Serial.println(httpResponseCode);
        String response = http.getString();
        Serial.println(response);
      } else {
        Serial.print("Error sending POST: ");
        Serial.println(httpResponseCode);
      }
      http.end();
    }
  }

  delay(5000); // Send data every 5 seconds
}