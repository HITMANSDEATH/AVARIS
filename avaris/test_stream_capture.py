#!/usr/bin/env python3
"""
Test Stream Capture Method
Tests capturing frames from the MJPEG stream as an alternative to the capture endpoint
"""

import requests
import time
import os

def test_stream_capture():
    """Test capturing a frame from the MJPEG stream"""
    print("🔍 Testing Stream Frame Capture")
    print("=" * 40)
    
    stream_url = "http://192.168.1.40/stream"
    
    try:
        print(f"Connecting to stream: {stream_url}")
        response = requests.get(stream_url, timeout=5, stream=True)
        
        if response.status_code != 200:
            print(f"❌ Stream failed: {response.status_code}")
            return False
        
        print("✅ Stream connected, extracting JPEG frame...")
        
        # Read stream data to find first JPEG
        jpeg_data = None
        buffer = b''
        bytes_read = 0
        
        for chunk in response.iter_content(chunk_size=1024):
            buffer += chunk
            bytes_read += len(chunk)
            
            # Look for JPEG start marker
            jpeg_start = buffer.find(b'\xff\xd8')
            if jpeg_start != -1:
                # Found JPEG start, now find end
                jpeg_end = buffer.find(b'\xff\xd9', jpeg_start)
                if jpeg_end != -1:
                    # Extract complete JPEG
                    jpeg_data = buffer[jpeg_start:jpeg_end + 2]
                    print(f"✅ JPEG frame found: {len(jpeg_data)} bytes")
                    break
            
            # Prevent reading too much
            if bytes_read > 1024 * 1024:  # 1MB limit
                print("⚠️  Reached 1MB limit, stopping")
                break
        
        if not jpeg_data:
            print("❌ No valid JPEG frame found in stream")
            return False
        
        if len(jpeg_data) < 1000:
            print(f"❌ JPEG too small: {len(jpeg_data)} bytes")
            return False
        
        # Save test image
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"stream_test_{timestamp}.jpg"
        
        with open(filename, 'wb') as f:
            f.write(jpeg_data)
        
        print(f"✅ Stream capture successful!")
        print(f"   Saved as: {filename}")
        print(f"   Size: {len(jpeg_data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Stream capture failed: {e}")
        return False

def test_direct_capture():
    """Test direct capture endpoint for comparison"""
    print("\n🔍 Testing Direct Capture Endpoint")
    print("=" * 40)
    
    capture_url = "http://192.168.1.40/capture"
    
    try:
        print(f"Testing: {capture_url}")
        start_time = time.time()
        
        response = requests.get(capture_url, timeout=15)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Direct capture successful ({elapsed:.2f}s)")
            print(f"   Size: {len(response.content)} bytes")
            
            # Save test image
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"direct_test_{timestamp}.jpg"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"   Saved as: {filename}")
            return True
        else:
            print(f"❌ Direct capture failed: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Direct capture timeout")
        return False
    except Exception as e:
        print(f"❌ Direct capture error: {e}")
        return False

def test_backend_with_fallback():
    """Test the backend with fallback method"""
    print("\n🔍 Testing Backend with Fallback")
    print("=" * 40)
    
    backend_url = "http://localhost:8000/api/capture-food-image"
    
    try:
        print("Sending capture request to backend...")
        start_time = time.time()
        
        response = requests.post(backend_url, timeout=60)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend capture successful ({elapsed:.2f}s)")
            print(f"   Food: {data.get('food_item')}")
            print(f"   Ingredients: {len(data.get('ingredients', []))} detected")
            print(f"   Risk: {data.get('risk_level')}")
            return True
        else:
            print(f"❌ Backend failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ESP32-CAM Stream Capture Test")
    print("=" * 50)
    
    tests = [
        ("Stream Capture", test_stream_capture),
        ("Direct Capture", test_direct_capture),
        ("Backend Fallback", test_backend_with_fallback),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
    
    if results.get("Stream Capture"):
        print("\n💡 Stream capture works! This provides a reliable fallback.")
    
    if results.get("Backend Fallback"):
        print("🎉 Backend with fallback is working!")
        print("   The Enter key should now work in the frontend.")
    else:
        print("⚠️  Backend still having issues. Check logs for details.")

if __name__ == "__main__":
    main()