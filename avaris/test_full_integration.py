#!/usr/bin/env python3
"""
Full AVARIS ESP32-CAM Integration Test
Tests the complete pipeline from camera to analysis
"""

import requests
import time
import json

# Configuration
ESP32_CAM_IP = "192.168.1.40"
BACKEND_API = "http://localhost:8000/api"

def test_esp32_cam_direct():
    """Test direct ESP32-CAM endpoints"""
    print("🔍 Testing ESP32-CAM Direct Access")
    print("=" * 50)
    
    # Test stream
    stream_url = f"http://{ESP32_CAM_IP}/stream"
    print(f"Stream URL: {stream_url}")
    
    try:
        response = requests.get(stream_url, timeout=3, stream=True)
        if response.status_code == 200:
            print("✅ Stream endpoint accessible")
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
        else:
            print(f"❌ Stream returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stream test failed: {e}")
        return False
    
    # Test capture
    capture_url = f"http://{ESP32_CAM_IP}/capture"
    print(f"\nCapture URL: {capture_url}")
    
    try:
        response = requests.get(capture_url, timeout=5)
        if response.status_code == 200:
            print("✅ Capture endpoint working")
            print(f"   Image size: {len(response.content)} bytes")
            
            # Save test image
            with open("direct_capture_test.jpg", "wb") as f:
                f.write(response.content)
            print("   Test image saved as direct_capture_test.jpg")
        else:
            print(f"❌ Capture returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Capture test failed: {e}")
        return False
    
    return True

def test_backend_integration():
    """Test AVARIS backend integration"""
    print("\n🔧 Testing AVARIS Backend Integration")
    print("=" * 50)
    
    # Test camera stream URL endpoint
    try:
        response = requests.get(f"{BACKEND_API}/camera/stream-url")
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend camera endpoint working")
            print(f"   Stream URL: {data.get('stream_url')}")
            print(f"   Available: {data.get('available')}")
        else:
            print(f"❌ Backend camera endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend camera endpoint error: {e}")
        return False
    
    # Test capture and analysis
    print("\n📸 Testing capture and analysis pipeline...")
    try:
        response = requests.post(f"{BACKEND_API}/capture-food-image", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Capture and analysis successful!")
            print(f"   Food Item: {data.get('food_item')}")
            print(f"   Ingredients: {data.get('ingredients')}")
            print(f"   Allergens: {data.get('detected_allergens')}")
            print(f"   Risk Level: {data.get('risk_level')}")
            print(f"   Confidence: {data.get('confidence')}")
            print(f"   Image URL: {data.get('image_url')}")
            
            # Save response for inspection
            with open("analysis_result.json", "w") as f:
                json.dump(data, f, indent=2)
            print("   Analysis result saved as analysis_result.json")
            
        else:
            print(f"❌ Capture and analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Capture and analysis timeout (>30s)")
        return False
    except Exception as e:
        print(f"❌ Capture and analysis error: {e}")
        return False
    
    return True

def test_frontend_compatibility():
    """Test frontend compatibility"""
    print("\n🌐 Testing Frontend Compatibility")
    print("=" * 50)
    
    # Test CORS and accessibility
    stream_url = f"http://{ESP32_CAM_IP}/stream"
    
    try:
        # Simulate frontend request
        headers = {
            'Origin': 'http://localhost:5173',
            'Referer': 'http://localhost:5173/'
        }
        
        response = requests.get(stream_url, headers=headers, timeout=3, stream=True)
        
        if response.status_code == 200:
            print("✅ Stream accessible from frontend origin")
            
            # Check CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            print("   CORS Headers:")
            for header, value in cors_headers.items():
                if value:
                    print(f"     {header}: {value}")
                else:
                    print(f"     {header}: Not set")
                    
        else:
            print(f"❌ Stream not accessible from frontend: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend compatibility test failed: {e}")
        return False
    
    return True

def run_full_test():
    """Run complete integration test"""
    print("🚀 AVARIS ESP32-CAM Full Integration Test")
    print("=" * 60)
    print(f"ESP32-CAM IP: {ESP32_CAM_IP}")
    print(f"Backend API: {BACKEND_API}")
    print("=" * 60)
    
    tests = [
        ("ESP32-CAM Direct Access", test_esp32_cam_direct),
        ("Backend Integration", test_backend_integration),
        ("Frontend Compatibility", test_frontend_compatibility),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Integration Test Results:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Full integration test successful!")
        print("   ESP32-CAM is ready for AVARIS frontend integration.")
        print("   You can now use the camera panel in the dashboard.")
    else:
        print("⚠️  Some tests failed. Check the following:")
        print("   - ESP32-CAM is powered and connected to WiFi")
        print("   - AVARIS backend is running (python main.py)")
        print("   - Camera and computer are on same network")
        print("   - Gemini API key is configured")
    
    return passed == total

if __name__ == "__main__":
    success = run_full_test()
    exit(0 if success else 1)