#!/usr/bin/env python3
"""
Test the ESP32-CAM capture fix
Verifies that the backend capture endpoint works properly
"""

import requests
import time

def test_backend_capture():
    """Test the fixed backend capture endpoint"""
    print("🔍 Testing Fixed Backend Capture Endpoint")
    print("=" * 50)
    
    backend_url = "http://localhost:8000/api/capture-food-image"
    
    print(f"Testing: {backend_url}")
    print("This should now work even if availability check times out...")
    
    try:
        print("\n📸 Sending capture request...")
        start_time = time.time()
        
        response = requests.post(backend_url, timeout=60)  # Generous timeout
        
        elapsed = time.time() - start_time
        print(f"⏱️  Request completed in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Capture successful!")
            print(f"   Food Item: {data.get('food_item')}")
            print(f"   Ingredients: {data.get('ingredients')}")
            print(f"   Allergens: {data.get('detected_allergens')}")
            print(f"   Risk Level: {data.get('risk_level')}")
            print(f"   Confidence: {data.get('confidence')}")
            print(f"   Image URL: {data.get('image_url')}")
            
            return True
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>60s)")
        print("   This suggests a deeper issue with Gemini API or processing")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        print("   Make sure backend is running: python main.py")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_direct_capture():
    """Test direct ESP32-CAM capture for comparison"""
    print("\n🔍 Testing Direct ESP32-CAM Capture")
    print("=" * 50)
    
    capture_url = "http://192.168.1.40/capture"
    
    try:
        print(f"Testing: {capture_url}")
        start_time = time.time()
        
        response = requests.get(capture_url, timeout=10)
        
        elapsed = time.time() - start_time
        print(f"⏱️  Direct capture completed in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            print(f"✅ Direct capture successful!")
            print(f"   Image size: {len(response.content)} bytes")
            
            # Save test image
            with open("direct_test_capture.jpg", "wb") as f:
                f.write(response.content)
            print("   Saved as: direct_test_capture.jpg")
            
            return True
        else:
            print(f"❌ Direct capture failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct capture error: {e}")
        return False

def main():
    """Run the capture tests"""
    print("🚀 ESP32-CAM Capture Fix Test")
    print("=" * 60)
    
    # Test direct capture first
    direct_ok = test_direct_capture()
    
    # Test backend capture
    backend_ok = test_backend_capture()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Direct ESP32-CAM: {'✅ PASS' if direct_ok else '❌ FAIL'}")
    print(f"   Backend Endpoint: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    
    if direct_ok and backend_ok:
        print("\n🎉 All tests passed!")
        print("   The Enter key capture should now work in the frontend.")
        print("   Try pressing Enter in the camera panel.")
    elif direct_ok and not backend_ok:
        print("\n⚠️  Direct capture works but backend fails.")
        print("   Check backend logs for detailed error information.")
        print("   Possible issues:")
        print("   - Gemini API key not configured")
        print("   - Database connection problems")
        print("   - Missing dependencies")
    else:
        print("\n❌ Tests failed.")
        print("   Check ESP32-CAM connection and network settings.")

if __name__ == "__main__":
    main()