#!/usr/bin/env python3
"""
Debug Camera Issues Script
Identifies and fixes common ESP32-CAM integration problems
"""

import requests
import time
import json
import subprocess
import sys

ESP32_CAM_IP = "192.168.1.40"
BACKEND_API = "http://localhost:8000/api"

def test_esp32_direct():
    """Test direct ESP32-CAM access"""
    print("🔍 Testing ESP32-CAM Direct Access")
    print("-" * 40)
    
    # Test stream
    stream_url = f"http://{ESP32_CAM_IP}/stream"
    print(f"Stream URL: {stream_url}")
    
    try:
        response = requests.get(stream_url, timeout=2, stream=True)
        if response.status_code == 200:
            print("✅ Stream endpoint accessible")
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            
            # Check if it's actually MJPEG
            if 'multipart' in content_type.lower():
                print("✅ Proper MJPEG stream detected")
            else:
                print("⚠️  Not standard MJPEG format, but may still work")
        else:
            print(f"❌ Stream failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stream test failed: {e}")
        return False
    
    # Test capture
    capture_url = f"http://{ESP32_CAM_IP}/capture"
    print(f"\nCapture URL: {capture_url}")
    
    try:
        start_time = time.time()
        response = requests.get(capture_url, timeout=10)
        capture_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Capture successful ({capture_time:.2f}s)")
            print(f"   Image size: {len(response.content)} bytes")
            
            # Save test image
            with open("debug_capture.jpg", "wb") as f:
                f.write(response.content)
            print("   Saved as debug_capture.jpg")
            
            return True
        else:
            print(f"❌ Capture failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Capture test failed: {e}")
        return False

def test_backend_api():
    """Test AVARIS backend API"""
    print("\n🔧 Testing AVARIS Backend API")
    print("-" * 40)
    
    # Test if backend is running
    try:
        response = requests.get(f"{BACKEND_API}/latest-sensor-data", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️  Backend responded with: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running! Start with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    
    # Test capture endpoint
    print("\n📸 Testing capture endpoint...")
    try:
        start_time = time.time()
        response = requests.post(f"{BACKEND_API}/capture-food-image", timeout=30)
        total_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Capture and analysis successful! ({total_time:.2f}s)")
            print(f"   Food: {data.get('food_item')}")
            print(f"   Ingredients: {len(data.get('ingredients', []))} detected")
            print(f"   Allergens: {data.get('detected_allergens')}")
            print(f"   Risk: {data.get('risk_level')}")
            
            # Save result
            with open("debug_analysis.json", "w") as f:
                json.dump(data, f, indent=2)
            print("   Analysis saved as debug_analysis.json")
            
            return True
        else:
            print(f"❌ Backend capture failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Backend capture timeout (>30s)")
        print("   This suggests Gemini API issues or slow processing")
        return False
    except Exception as e:
        print(f"❌ Backend capture error: {e}")
        return False

def test_stream_performance():
    """Test stream loading performance"""
    print("\n⚡ Testing Stream Performance")
    print("-" * 40)
    
    stream_url = f"http://{ESP32_CAM_IP}/stream"
    
    # Test initial load time
    try:
        start_time = time.time()
        response = requests.get(stream_url, timeout=5, stream=True)
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Stream loads in {load_time:.2f}s")
            
            # Test with timestamp (cache busting)
            timestamp_url = f"{stream_url}?t={int(time.time())}"
            start_time = time.time()
            response2 = requests.get(timestamp_url, timeout=5, stream=True)
            timestamp_load_time = time.time() - start_time
            
            print(f"✅ Timestamp URL loads in {timestamp_load_time:.2f}s")
            
            if load_time > 2.0:
                print("⚠️  Stream loading is slow (>2s)")
                print("   Suggestions:")
                print("   - Check WiFi signal strength")
                print("   - Reduce ESP32-CAM JPEG quality")
                print("   - Use wired connection if possible")
            else:
                print("✅ Stream loading is fast")
                
            return True
        else:
            print(f"❌ Stream performance test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stream performance test error: {e}")
        return False

def check_frontend_issues():
    """Check common frontend issues"""
    print("\n🌐 Checking Frontend Issues")
    print("-" * 40)
    
    # Check if frontend is running
    try:
        response = requests.get("http://localhost:5173", timeout=3)
        if response.status_code == 200:
            print("✅ Frontend is running on port 5173")
        else:
            print(f"⚠️  Frontend responded with: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Frontend not running! Start with: cd frontend && npm run dev")
        return False
    except Exception as e:
        print(f"❌ Frontend check failed: {e}")
        return False
    
    # Check CORS issues
    print("\n🔒 Testing CORS...")
    try:
        headers = {
            'Origin': 'http://localhost:5173',
            'Referer': 'http://localhost:5173/'
        }
        response = requests.get(f"http://{ESP32_CAM_IP}/stream", headers=headers, timeout=3, stream=True)
        
        if response.status_code == 200:
            print("✅ No CORS issues detected")
        else:
            print(f"⚠️  Possible CORS issue: {response.status_code}")
    except Exception as e:
        print(f"⚠️  CORS test inconclusive: {e}")
    
    return True

def provide_solutions():
    """Provide solutions for common issues"""
    print("\n💡 Common Solutions")
    print("-" * 40)
    
    print("🔧 If Enter key doesn't work:")
    print("   - Check browser console for JavaScript errors")
    print("   - Ensure camera panel is focused")
    print("   - Try clicking on the stream first")
    print("   - Test with the debug HTML file: test_enter_key.html")
    
    print("\n🔧 If stream loads slowly:")
    print("   - Reduce refresh interval (currently 100ms)")
    print("   - Check ESP32-CAM power supply (use 5V)")
    print("   - Improve WiFi signal strength")
    print("   - Use lower JPEG quality on ESP32-CAM")
    
    print("\n🔧 If capture fails:")
    print("   - Check Gemini API key configuration")
    print("   - Verify ESP32-CAM capture endpoint works")
    print("   - Check backend logs for errors")
    print("   - Ensure uploads/avaris_cam/ directory exists")
    
    print("\n🔧 If stream doesn't appear:")
    print("   - Check browser network tab for failed requests")
    print("   - Try direct stream URL in browser")
    print("   - Verify ESP32-CAM IP address (192.168.1.40)")
    print("   - Check if ESP32-CAM and computer are on same network")

def main():
    """Run complete diagnostic"""
    print("🚀 AVARIS ESP32-CAM Debug Tool")
    print("=" * 50)
    
    tests = [
        ("ESP32-CAM Direct", test_esp32_direct),
        ("Backend API", test_backend_api),
        ("Stream Performance", test_stream_performance),
        ("Frontend Check", check_frontend_issues),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Debug Results:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed < total:
        provide_solutions()
    else:
        print("🎉 All tests passed! System should be working correctly.")
        print("\n📋 Next steps:")
        print("   1. Open frontend: http://localhost:5173")
        print("   2. Click 'AVARIS Cam' button")
        print("   3. Wait for stream to load")
        print("   4. Press Enter to capture")
        print("   5. Check Food Analysis Panel for results")

if __name__ == "__main__":
    main()