"""
ESP32-CAM Integration Module
Handles live stream and image capture from ESP32-CAM
"""

import requests
import os
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ESP32Camera:
    """ESP32-CAM controller for live streaming and image capture"""
    
    def __init__(self, camera_ip: str = "192.168.1.40"):
        self.camera_ip = camera_ip
        self.stream_url = f"http://{camera_ip}/stream"
        self.capture_url = f"http://{camera_ip}/capture"
        self.led_on_url = f"http://{camera_ip}/led/on"
        self.led_off_url = f"http://{camera_ip}/led/off"
        self.upload_dir = "uploads/avaris_cam"
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        
        logger.info(f"ESP32-CAM initialized at {camera_ip}")
    
    def is_available(self) -> bool:
        """Check if ESP32-CAM is reachable"""
        try:
            # Use a very short timeout and try the capture endpoint
            response = requests.get(self.capture_url, timeout=1)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"ESP32-CAM availability check failed: {e}")
            # Don't fail completely - the camera might still work for capture
            return True  # Assume available and let capture method handle errors
    
    def turn_led_on(self) -> bool:
        """Turn on ESP32-CAM LED (GPIO4)"""
        try:
            response = requests.get(self.led_on_url, timeout=0.5)  # Very short timeout
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to turn LED on: {e}")
            return False
    
    def turn_led_off(self) -> bool:
        """Turn off ESP32-CAM LED (GPIO4)"""
        try:
            response = requests.get(self.led_off_url, timeout=0.5)  # Very short timeout
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Failed to turn LED off: {e}")
            return False
    
    def capture_image(self, use_flash: bool = True) -> dict:
        """
        Capture image from ESP32-CAM
        Stream should be paused by frontend to prevent conflicts
        
        Args:
            use_flash (bool): Whether to use LED flash before capture
            
        Returns:
            dict: {
                "success": bool,
                "image_path": str,
                "error": str (if failed)
            }
        """
        try:
            # Optional: Turn on LED flash
            if use_flash:
                try:
                    self.turn_led_on()
                    time.sleep(0.2)  # Wait 200ms for LED to illuminate
                except Exception as e:
                    logger.warning(f"LED flash failed, continuing without: {e}")
            
            # Capture image from ESP32-CAM with generous timeout
            logger.info(f"Capturing image from ESP32-CAM at {self.capture_url}")
            response = requests.get(self.capture_url, timeout=20)  # Generous timeout
            
            # Turn off LED (best effort)
            if use_flash:
                try:
                    self.turn_led_off()
                except Exception as e:
                    logger.warning(f"LED turn off failed: {e}")
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"ESP32-CAM returned status {response.status_code}"
                }
            
            # Check if we got actual image data
            if len(response.content) < 1000:  # Very small response suggests error
                return {
                    "success": False,
                    "error": f"ESP32-CAM returned very small response ({len(response.content)} bytes)"
                }
            
            # Save image with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cam_capture_{timestamp}.jpg"
            file_path = os.path.join(self.upload_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Image captured successfully: {file_path} ({len(response.content)} bytes)")
            
            return {
                "success": True,
                "image_path": file_path,
                "filename": filename
            }
            
        except requests.exceptions.Timeout:
            logger.error("ESP32-CAM capture timeout")
            return {
                "success": False,
                "error": "ESP32-CAM capture timeout. Camera may be busy or network is slow."
            }
        except requests.exceptions.ConnectionError:
            logger.error("ESP32-CAM connection error")
            return {
                "success": False,
                "error": "Cannot connect to ESP32-CAM. Check IP address and network connection."
            }
        except Exception as e:
            logger.error(f"Error capturing image from ESP32-CAM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def capture_from_stream(self) -> dict:
        """
        Alternative capture method using the MJPEG stream
        This can be more reliable than the dedicated capture endpoint
        """
        try:
            logger.info(f"Capturing frame from MJPEG stream at {self.stream_url}")
            
            # Get stream data
            response = requests.get(self.stream_url, timeout=5, stream=True)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Stream returned status {response.status_code}"
                }
            
            # Read the first JPEG frame from the MJPEG stream
            boundary = None
            content_type = response.headers.get('content-type', '')
            
            if 'boundary=' in content_type:
                boundary = content_type.split('boundary=')[1].strip()
            
            # Read stream data to find first JPEG
            jpeg_data = None
            buffer = b''
            
            for chunk in response.iter_content(chunk_size=1024):
                buffer += chunk
                
                # Look for JPEG start marker
                jpeg_start = buffer.find(b'\xff\xd8')
                if jpeg_start != -1:
                    # Found JPEG start, now find end
                    jpeg_end = buffer.find(b'\xff\xd9', jpeg_start)
                    if jpeg_end != -1:
                        # Extract complete JPEG
                        jpeg_data = buffer[jpeg_start:jpeg_end + 2]
                        break
                
                # Prevent buffer from growing too large
                if len(buffer) > 1024 * 1024:  # 1MB limit
                    buffer = buffer[-512 * 1024:]  # Keep last 512KB
            
            if not jpeg_data or len(jpeg_data) < 1000:
                return {
                    "success": False,
                    "error": "Could not extract valid JPEG from stream"
                }
            
            # Save image with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stream_capture_{timestamp}.jpg"
            file_path = os.path.join(self.upload_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(jpeg_data)
            
            logger.info(f"Frame captured from stream: {file_path} ({len(jpeg_data)} bytes)")
            
            return {
                "success": True,
                "image_path": file_path,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error capturing from stream: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def capture_image_with_fallback(self, use_flash: bool = True) -> dict:
        """
        Capture image with fallback to stream method
        """
        # First try the dedicated capture endpoint
        result = self.capture_image(use_flash)
        
        if result["success"]:
            return result
        
        logger.warning("Dedicated capture failed, trying stream capture...")
        
        # Fallback to stream capture
        stream_result = self.capture_from_stream()
        
        if stream_result["success"]:
            logger.info("Stream capture successful as fallback")
            return stream_result
        
        # Both methods failed
        return {
            "success": False,
            "error": f"Both capture methods failed. Capture: {result['error']}. Stream: {stream_result['error']}"
        }
    
    def get_stream_url(self) -> str:
        """Get the MJPEG stream URL"""
        return self.stream_url

# Global camera instance
_esp32_camera = None

def get_esp32_camera(camera_ip: str = None) -> ESP32Camera:
    """Get the global ESP32 camera instance"""
    global _esp32_camera
    if _esp32_camera is None:
        # Use the specific IP address provided
        ip = camera_ip or "192.168.1.40"
        _esp32_camera = ESP32Camera(ip)
    return _esp32_camera

def capture_from_esp32(use_flash: bool = True) -> dict:
    """
    Convenience function to capture image from ESP32-CAM
    
    Args:
        use_flash (bool): Whether to use LED flash
        
    Returns:
        dict: Capture result
    """
    camera = get_esp32_camera()
    return camera.capture_image(use_flash)
