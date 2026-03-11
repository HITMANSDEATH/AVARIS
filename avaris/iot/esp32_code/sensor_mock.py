import time
import requests
import random
import datetime
import os

API_URL = "http://localhost:8000/api/sensor-data"

def simulate_sensor_data():
    """Simulates an ESP32 sending environmental data to the AVARIS backend."""
    
    print(f"Starting ESP32 Sensor Simulation. Sending data to {API_URL}")
    print("Press Ctrl+C to stop.")
    
    # Initial "normal" values
    temp = 25.0
    hum = 45.0
    dust = 30.0

    try:
        while True:
            # Simulate a 10% chance of an "anomaly" (e.g., someone started smoking, a fire, or AC broke)
            if random.random() < 0.10:
                print("\n[!] Simulating Anomalous Event (Spike in Temperature and Dust) [!]")
                temp += random.uniform(10, 20)  # Sudden heat spike
                dust += random.uniform(150, 300) # Sudden dust/smoke spike
                hum -= random.uniform(5, 15)    # Drop in humidity
            else:
                # Drift back towards normal slowly, or fluctuate normally
                temp += random.uniform(-0.5, 0.5)
                temp = max(15.0, min(temp, 30.0)) # keep somewhat realistic if not anomaly
                
                hum += random.uniform(-1.0, 1.0)
                hum = max(30.0, min(hum, 60.0))
                
                dust += random.uniform(-2.0, 2.0)
                dust = max(10.0, min(dust, 60.0))

            payload = {
                "temperature": round(temp, 2),
                "humidity": round(hum, 2),
                "dust": round(dust, 2),
                "timestamp": datetime.datetime.utcnow().isoformat()
            }

            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    print(f"Sent: Temp={payload['temperature']}°C, Hum={payload['humidity']}%, Dust={payload['dust']}ug/m3 | "
                          f"AI Risk: {data.get('risk_level', 'UNKNOWN')} | Anomaly: {data.get('anomaly_detected', False)}")
                else:
                    print(f"Failed to send data. Status code: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"Connection error. Is the AVARIS backend running at {API_URL}?")

            time.sleep(5) # Send data every 5 seconds

    except KeyboardInterrupt:
        print("\nStopping sensor simulation.")

if __name__ == "__main__":
    simulate_sensor_data()
