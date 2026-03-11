import cv2
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
import time
import numpy as np

app = FastAPI()

def generate_frames():
    """
    Simulate an ESP32-CAM video stream.
    Instead of connecting to real hardware, we generate a video feed 
    with a moving environmental overlay to demonstrate the functionality.
    """
    width, height = 640, 480
    frame_count = 0
    
    while True:
        # Create a blank image
        frame = np.zeros((height, width, 3), np.uint8)
        
        # Add a moving gradient background for "movement" effect
        bg_color = int((np.sin(frame_count * 0.05) + 1) * 127)
        frame[:] = (bg_color // 3, bg_color // 2, bg_color)
        
        # Overlay Mock Sensor Data
        cv2.putText(frame, "AVARIS ESP32-CAM MOCK FEED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, f"Temp: {min(25 + np.sin(frame_count * 0.1) * 5, 50):.1f} C", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, f"Smoke Dust: {max(30 + np.cos(frame_count * 0.2) * 20, 0):.0f} ug", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, f"Status: Monitoring", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        # Draw a "scanning" line
        scan_y = int((frame_count * 5) % height)
        cv2.line(frame, (0, scan_y), (width, scan_y), (0, 0, 255), 2)

        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Yield stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
               
        frame_count += 1
        time.sleep(0.1) # 10 FPS roughly

@app.get("/stream")
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    print("Starting MOCK ESP32-CAM Server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
