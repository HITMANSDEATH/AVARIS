#!/usr/bin/env python3
"""
Test script for ESP32 sensor polling functionality
Tests both ESP32 /sensors endpoint and backend polling service
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
ESP32_IP = "192.168.1.40"  # Update with your ESP32 IP
BACKEND_URL = "http://localhost:8000"

async def test_esp32_direct():
    """Test ESP32 /sensors endpoint directly"""
    print("=== Testing ESP32 Direct Access ===")
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"http://{ESP32_IP}/sensors")
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ ESP32 Response: {json.dumps(data, indent=2)}")
            
            # Validate data structure
            required_fields = ['temperature', 'humidity', 'dust']
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing field: {field}")
                    return False
                    
            print(f"🌡️  Temperature: {data['temperature']}°C")
            print(f"💧 Humidity: {data['humidity']}%")
            print(f"🌫️  Dust: {data['dust']}µg/m³")
            return True
            
    except httpx.ConnectError:
        print(f"❌ Cannot connect to ESP32 at {ESP32_IP}")
        print("   Make sure ESP32 is powered on and connected to WiFi")
        return False
    except httpx.TimeoutException:
        print(f"❌ Timeout connecting to ESP32 at {ESP32_IP}")
        return False
    except Exception as e:
        print(f"❌ Error testing ESP32: {e}")
        return False

async def test_backend_polling():
    """Test backend /api/latest-sensors endpoint"""
    print("\n=== Testing Backend Polling Service ===")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BACKEND_URL}/api/latest-sensors")
            response.raise_for_status()
            
            data = response.json()
            print(f"✅ Backend Response: {json.dumps(data, indent=2)}")
            
            print(f"🌡️  Temperature: {data['temperature']}°C")
            print(f"💧 Humidity: {data['humidity']}%")
            print(f"🌫️  Dust: {data['dust']}µg/m³")
            print(f"⏰ Timestamp: {data['timestamp']}")
            return True
            
    except httpx.ConnectError:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print("   Make sure AVARIS backend is running")
        return False
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 503:
            print("❌ Backend reports sensor data unavailable")
            print("   ESP32 may be offline or data is stale")
        else:
            print(f"❌ Backend HTTP error: {e.response.status_code}")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

async def main():
    """Run all tests"""
    print("AVARIS Sensor Polling Test")
    print("=" * 40)
    
    # Test ESP32 directly first
    esp32_ok = await test_esp32_direct()
    
    # Wait a moment for backend to poll
    if esp32_ok:
        print("\n⏳ Waiting 10 seconds for backend to poll...")
        await asyncio.sleep(10)
    
    # Test backend polling service
    backend_ok = await test_backend_polling()
    
    print("\n" + "=" * 40)
    if esp32_ok and backend_ok:
        print("✅ All tests passed! Sensor polling is working correctly.")
    elif esp32_ok:
        print("⚠️  ESP32 works but backend polling has issues")
    else:
        print("❌ ESP32 connection failed - check hardware and network")

if __name__ == "__main__":
    asyncio.run(main())