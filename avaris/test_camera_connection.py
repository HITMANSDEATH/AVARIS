#!/usr/bin/env python3
"""
Simple ESP32-CAM Connection Test
Tests the specific camera at 192.168.1.40
"""

import requests
import time

ESP32_CAM_IP = "192.168.1.40"
STREAM_URL = f"http://{ESP32_CAM_IP}/stream"
CAPTURE_URL = f"http://{ESP32_CAM_IP}/capture"

def test_camera_connection():
    """Test basic camera connectivity"""
    print(f"🔍 Testing ESP32-CAM at {ESP32_CAM_IP}")
    print(f"Stream URL: {STREAM_URL}")
    print(f"Capture URL: {CAPTURE_URL}")
    
    try:
        # Test capture endpoint
        print("\n📸 Testing capture endpoint...")
        response = requests.get(CAPTURE_URL, timeout=5)
        
        if response.status_code == 200:
            print("✅ Capture endpoint is working")
            print(f"   Response size: {len(response.content)} bytes")
            
            # Save test image
            with open("test_capture.jpg", "wb") as f:
                f.write(response.content)
            print("   Test image saved as test_capture.jpg")
            
        else:
            print(f"❌ Capture endpoint returned status: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - camera not responding")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    try:
        # Test stream endpoint (just check if it responds)
        print("\n🎥 Testing stream endpoint...")
        response = requests.get(STREAM_URL, timeout=3, stream=True)
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            print("✅ Stream endpoint is accessible")
            print(f"   Content-Type: {content_type}")
            
            if 'multipart' in content_type.lower() or 'image' in content_type.lower():
                print("✅ MJPEG stream format detected")
            else:
                print(f"⚠️  Unexpected content type: {content_type}")
                
        else:
            print(f"❌ Stream endpoint returned status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stream test error: {e}")
        return False
    
    print("\n🎉 Camera connection test successful!")
    print("The ESP32-CAM is ready for AVARIS integration.")
    return True

if __name__ == "__main__":
    success = test_camera_connection()
    if not success:
        print("\n⚠️  Camera connection failed. Please check:")
        print("   - ESP32-CAM is powered on")
        print("   - WiFi connection is working")
        print("   - IP address is correct (192.168.1.40)")
        print("   - Camera and computer are on same network")
    exit(0 if success else 1)