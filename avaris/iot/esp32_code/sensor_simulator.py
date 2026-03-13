#!/usr/bin/env python3
"""
Sensor Data Simulator for AVARIS Backend Testing
Simulates ESP32 sensor readings and sends them to the AVARIS backend
"""

import requests
import json
import time
import random
from datetime import datetime
import argparse

class SensorSimulator:
    def __init__(self, server_url="http://localhost:8000", interval=30):
        self.server_url = server_url.rstrip('/')
        self.sensor_endpoint = f"{self.server_url}/api/sensor-data"
        self.health_endpoint = f"{self.server_url}/api/sensor-data/health"
        self.interval = interval
        self.running = False
        
    def generate_realistic_data(self):
        """Generate realistic sensor data with some variation"""
        base_time = datetime.now()
        
        # Base values with realistic ranges
        base_temp = 22.0 + random.uniform(-3, 8)  # 19-30°C
        base_humidity = 50.0 + random.uniform(-15, 25)  # 35-75%
        base_dust = 25.0 + random.uniform(-10, 40)  # 15-65 µg/m³
        
        # Add some correlation (higher temp = lower humidity, dust varies)
        if base_temp > 25:
            base_humidity *= 0.9  # Hot air holds less moisture
        
        # Ensure realistic bounds
        temperature = max(15.0, min(35.0, base_temp))
        humidity = max(20.0, min(80.0, base_humidity))
        dust = max(0.0, min(150.0, base_dust))
        
        return {
            "temperature": round(temperature, 1),
            "humidity": round(humidity, 1),
            "dust": round(dust, 1),
            "timestamp": base_time.isoformat()
        }
    
    def generate_extreme_data(self):
        """Generate extreme sensor data for testing"""
        scenarios = [
            {"temperature": 35.5, "humidity": 85.0, "dust": 120.0, "name": "High Risk"},
            {"temperature": 12.0, "humidity": 15.0, "dust": 80.0, "name": "Cold & Dusty"},
            {"temperature": 40.0, "humidity": 90.0, "dust": 150.0, "name": "Critical"},
            {"temperature": 8.0, "humidity": 95.0, "dust": 200.0, "name": "Extreme"},
        ]
        
        scenario = random.choice(scenarios)
        return {
            "temperature": scenario["temperature"],
            "humidity": scenario["humidity"],
            "dust": scenario["dust"],
            "timestamp": datetime.now().isoformat(),
            "_scenario": scenario["name"]
        }
    
    def send_sensor_data(self, data):
        """Send sensor data to AVARIS backend"""
        try:
            # Remove internal fields
            clean_data = {k: v for k, v in data.items() if not k.startswith('_')}
            
            response = requests.post(
                self.sensor_endpoint,
                json=clean_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Data sent successfully!")
                print(f"   Temperature: {clean_data['temperature']}°C")
                print(f"   Humidity: {clean_data['humidity']}%")
                print(f"   Dust: {clean_data['dust']}µg/m³")
                print(f"   Risk Level: {result.get('risk_level', 'UNKNOWN')}")
                
                if '_scenario' in data:
                    print(f"   Scenario: {data['_scenario']}")
                
                return True
            else:
                print(f"❌ Server error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection failed - is AVARIS backend running?")
            return False
        except requests.exceptions.Timeout:
            print("❌ Request timeout")
            return False
        except Exception as e:
            print(f"❌ Error sending data: {e}")
            return False
    
    def check_server_health(self):
        """Check if AVARIS backend is healthy"""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print("✅ AVARIS Backend is healthy")
                print(f"   Server: {self.server_url}")
                print(f"   Status: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"⚠️ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot reach AVARIS backend: {e}")
            return False
    
    def run_continuous(self):
        """Run continuous sensor simulation"""
        print(f"🚀 Starting AVARIS Sensor Simulator")
        print(f"   Server: {self.server_url}")
        print(f"   Interval: {self.interval} seconds")
        print(f"   Press Ctrl+C to stop")
        print("-" * 50)
        
        # Check server health first
        if not self.check_server_health():
            print("❌ Cannot connect to AVARIS backend. Please check:")
            print("   1. Backend server is running (python main.py)")
            print("   2. Server URL is correct")
            print("   3. Network connectivity")
            return
        
        self.running = True
        reading_count = 0
        
        try:
            while self.running:
                reading_count += 1
                print(f"\n📊 Reading #{reading_count} at {datetime.now().strftime('%H:%M:%S')}")
                
                # Generate and send data
                data = self.generate_realistic_data()
                success = self.send_sensor_data(data)
                
                if success:
                    print(f"⏰ Next reading in {self.interval} seconds...")
                else:
                    print(f"⚠️ Failed to send data, retrying in {self.interval} seconds...")
                
                # Wait for next reading
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping sensor simulator...")
            self.running = False
    
    def send_test_batch(self, count=5):
        """Send a batch of test readings"""
        print(f"🧪 Sending {count} test readings...")
        
        if not self.check_server_health():
            return
        
        for i in range(count):
            print(f"\n📊 Test Reading {i+1}/{count}")
            
            # Mix normal and extreme data
            if random.random() < 0.3:  # 30% chance of extreme conditions
                data = self.generate_extreme_data()
                print(f"   🚨 Generating extreme scenario: {data.get('_scenario', 'Unknown')}")
            else:
                data = self.generate_realistic_data()
                print(f"   📈 Generating normal reading")
            
            self.send_sensor_data(data)
            
            if i < count - 1:  # Don't wait after last reading
                time.sleep(2)  # Short delay between test readings
        
        print(f"\n✅ Completed {count} test readings")

def main():
    parser = argparse.ArgumentParser(description="AVARIS Sensor Data Simulator")
    parser.add_argument("--server", default="http://localhost:8000", 
                       help="AVARIS backend server URL")
    parser.add_argument("--interval", type=int, default=30,
                       help="Interval between readings in seconds")
    parser.add_argument("--mode", choices=["continuous", "test", "health"], 
                       default="continuous",
                       help="Simulation mode")
    parser.add_argument("--count", type=int, default=5,
                       help="Number of test readings (test mode only)")
    
    args = parser.parse_args()
    
    simulator = SensorSimulator(args.server, args.interval)
    
    if args.mode == "continuous":
        simulator.run_continuous()
    elif args.mode == "test":
        simulator.send_test_batch(args.count)
    elif args.mode == "health":
        simulator.check_server_health()

if __name__ == "__main__":
    main()