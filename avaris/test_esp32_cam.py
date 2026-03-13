#!/usr/bin/env python3
"""
ESP32-CAM Integration Test Script
Tests camera connectivity, streaming, and capture functionality
"""

import requests
import time
import os
from backend.camera.esp32_cam import get_esp32_camera
from backend.config.settings import settings

def test_camera_connectivity():
    """Test basic ESP32-CAM connectivity"""
    print("🔍 Testing ESP32-CAM Connectivity...")
    
    camera = get_esp32_camera()
    print(f"Camera IP: {camera.camera_ip}")
    print(f"Stream URL: {camera.stream_url}")
    print(f"Capture URL: {camera.capture_url}")
    
    # Test basic connectivity
    if camera.is_available():
        print("✅ ESP32-CAM is reachable")
        return True
    else:
        print("❌ ESP32-CAM is not reachable")
        print("   Check:")
        print("   - WiFi connection")
        print("   - IP address configuration")
        print("   - Power supply")
        return False

def test_led_control():
    """Test LED flash control"""
    print("\n💡 Testing LED Control...")
    
    camera = get_esp32_camera()
    
    try:
        # Turn LED on
        print("Turning LED ON...")
        if camera.turn_led_on():
            print("✅ LED turned ON successfully")
            time.sleep(1)
        else:
            print("❌ Failed to turn LED ON")
            return False
        
        # Turn LED off
        print("Turning LED OFF...")
        if camera.turn_led_off():
            print("✅ LED turned OFF successfully")
            return True
        else:
            print("❌ Failed to turn LED OFF")
            return False
            
    except Exception as e:
        print(f"❌ LED control error: {e}")
        return False

def test_image_capture():
    """Test image capture functionality"""
    print("\n📸 Testing Image Capture...")
    
    camera = get_esp32_camera()
    
    try:
        # Capture image with flash
        print("Capturing image with LED flash...")
        result = camera.capture_image(use_flash=True)
        
        if result["success"]:
            print(f"✅ Image captured successfully: {result['image_path']}")
            
            # Check if file exists and has content
            if os.path.exists(result["image_path"]):
                file_size = os.path.getsize(result["image_path"])
                print(f"   File size: {file_size} bytes")
                
                if file_size > 1000:  # Reasonable minimum for JPEG
                    print("✅ Image file appears valid")
                    return True
                else:
                    print("❌ Image file too small, may be corrupted")
                    return False
            else:
                print("❌ Image file not found")
                return False
        else:
            print(f"❌ Image capture failed: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Image capture error: {e}")
        return False

def test_stream_access():
    """Test MJPEG stream accessibility"""
    print("\n🎥 Testing MJPEG Stream...")
    
    camera = get_esp32_camera()
    
    try:
        # Try to access stream (just check if endpoint responds)
        response = requests.get(camera.stream_url, timeout=5, stream=True)
        
        if response.status_code == 200:
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'multipart' in content_type.lower():
                print("✅ MJPEG stream is accessible")
                print(f"   Content-Type: {content_type}")
                return True
            else:
                print(f"❌ Unexpected content type: {content_type}")
                return False
        else:
            print(f"❌ Stream returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Stream access timeout")
        return False
    except Exception as e:
        print(f"❌ Stream access error: {e}")
        return False

def test_camera_status():
    """Test camera status endpoint"""
    print("\n📊 Testing Camera Status...")
    
    camera = get_esp32_camera()
    status_url = f"http://{camera.camera_ip}/status"
    
    try:
        response = requests.get(status_url, timeout=3)
        
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Status endpoint accessible")
            print(f"   Camera initialized: {status_data.get('camera_initialized', 'Unknown')}")
            print(f"   WiFi connected: {status_data.get('wifi_connected', 'Unknown')}")
            print(f"   IP address: {status_data.get('ip_address', 'Unknown')}")
            return True
        else:
            print(f"❌ Status endpoint returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def run_full_test():
    """Run complete ESP32-CAM test suite"""
    print("🚀 AVARIS ESP32-CAM Integration Test")
    print("=" * 50)
    
    tests = [
        ("Connectivity", test_camera_connectivity),
        ("Status Check", test_camera_status),
        ("LED Control", test_led_control),
        ("Image Capture", test_image_capture),
        ("Stream Access", test_stream_access),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ESP32-CAM is ready for AVARIS integration.")
    else:
        print("⚠️  Some tests failed. Check ESP32-CAM setup and configuration.")
        print("   Refer to ESP32_CAM_SETUP.md for troubleshooting.")
    
    return passed == total

if __name__ == "__main__":
    success = run_full_test()
    exit(0 if success else 1)