#!/usr/bin/env python3
"""
Quick ESP32-CAM Setup Verification
Verifies the camera is properly configured for AVARIS
"""

import requests
import sys

def verify_setup():
    """Verify ESP32-CAM setup for AVARIS"""
    print("🔍 AVARIS ESP32-CAM Setup Verification")
    print("=" * 45)
    
    ESP32_IP = "192.168.1.40"
    
    print(f"Testing ESP32-CAM at: {ESP32_IP}")
    print(f"Expected stream URL: http://{ESP32_IP}/stream")
    print(f"Expected capture URL: http://{ESP32_IP}/capture")
    
    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"http://{ESP32_IP}/capture", timeout=3)
        if response.status_code == 200:
            print("   ✅ ESP32-CAM is reachable")
            print(f"   📏 Response size: {len(response.content)} bytes")
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
    except requests.exceptions.ConnectTimeout:
        print("   ❌ Connection timeout - camera not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection refused - check IP address and network")
        return False
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False
    
    # Test 2: Stream format
    print("\n2. Testing stream format...")
    try:
        response = requests.get(f"http://{ESP32_IP}/stream", timeout=2, stream=True)
        content_type = response.headers.get('content-type', '').lower()
        
        if 'multipart' in content_type or 'image' in content_type:
            print("   ✅ MJPEG stream format detected")
            print(f"   📋 Content-Type: {content_type}")
        else:
            print(f"   ⚠️  Unexpected format: {content_type}")
            print("   💡 Stream may still work in browser")
            
    except Exception as e:
        print(f"   ⚠️  Stream test failed: {e}")
        print("   💡 This may be normal for MJPEG streams")
    
    # Test 3: Image quality
    print("\n3. Testing image quality...")
    try:
        response = requests.get(f"http://{ESP32_IP}/capture", timeout=5)
        if response.status_code == 200:
            size = len(response.content)
            if size > 5000:  # Reasonable minimum for a decent JPEG
                print(f"   ✅ Good image quality ({size} bytes)")
            elif size > 1000:
                print(f"   ⚠️  Small image size ({size} bytes) - check lighting")
            else:
                print(f"   ❌ Very small image ({size} bytes) - possible issue")
                return False
    except Exception as e:
        print(f"   ❌ Image quality test failed: {e}")
        return False
    
    print("\n" + "=" * 45)
    print("✅ ESP32-CAM setup verification PASSED!")
    print("\n📋 Next steps:")
    print("   1. Start AVARIS backend: python main.py")
    print("   2. Start frontend: cd frontend && npm run dev")
    print("   3. Click 'AVARIS Cam' button in dashboard")
    print("   4. Press Enter to capture and analyze food")
    
    print("\n🔧 If stream doesn't appear in frontend:")
    print("   - Open browser developer tools")
    print("   - Check for CORS or network errors")
    print("   - Try the test HTML: test_mjpeg_stream.html")
    
    return True

if __name__ == "__main__":
    success = verify_setup()
    if not success:
        print("\n❌ Setup verification FAILED!")
        print("\n🔧 Troubleshooting:")
        print("   - Check ESP32-CAM power supply")
        print("   - Verify WiFi connection")
        print("   - Confirm IP address (192.168.1.40)")
        print("   - Ensure same network as computer")
        sys.exit(1)
    else:
        sys.exit(0)