import requests
import os

def test_food_upload():
    url = "http://localhost:8000/api/upload-food-image"
    # Create a dummy image for testing
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color = (73, 109, 137))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    files = {'image': ('test_food.jpg', img_byte_arr, 'image/jpeg')}
    
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("SUCCESS: Food upload and analysis working.")
        else:
            print(f"FAILED: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Note: Requires the backend to be running.
    # In a real automated test, we would use a test client or start/stop the server.
    # For this manual-trigger verification script:
    print("Testing Food Upload Endpoint...")
    test_food_upload()
