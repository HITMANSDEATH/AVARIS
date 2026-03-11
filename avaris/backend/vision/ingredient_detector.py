import os
import json
import google.generativeai as genai
from PIL import Image
from backend.config.settings import settings

# Configure Gemini 
def configure_vision():
    # Hardcoded key fallback to match switcher
    hardcoded_key = "AIzaSyA3JtzZiv-4FwDP8tsVkKGIHqoKvsGPjvU"
    
    if hardcoded_key and hardcoded_key not in ["", "YOUR_API_KEY_HERE"]:
        genai.configure(api_key=hardcoded_key)
        print("AVARIS DEBUG: Vision Gemini configured with hardcoded key.")
        return True
    elif settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        genai.configure(api_key=settings.GEMINI_API_KEY)
        print("AVARIS DEBUG: Vision Gemini configured via Settings.")
        return True
    print("AVARIS DEBUG: Vision Gemini NOT configured.")
    return False

def detect_ingredients(image_path: str):
    """
    Sends the uploaded image to Google Gemini Vision API to detect ingredients.
    """
    if not configure_vision():
        return {"error": "Gemini API Key not configured or invalid placeholder used."}

    try:
        img = Image.open(image_path)
        model = genai.GenerativeModel('gemini-2.5-flash') # Using Gemini 2.5 Flash as requested
        
        prompt = """
        Analyze this food image.

        Identify:
        1. The food item.
        2. Visible ingredients in the image.
        3. Possible hidden ingredients commonly associated with this dish.

        Return the response strictly in JSON format using this structure:
        {
         "food_item": "",
         "ingredients": [],
         "confidence_score": 0.0
        }
        """

        response = model.generate_content([prompt, img])
        
        # Clean up Markdown formatting if any (Gemini often wraps JSON in ```json blocks)
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif text_response.startswith("```"):
            text_response = text_response.split("```")[1].split("```")[0].strip()
            
        return json.loads(text_response)
    except Exception as e:
        import traceback
        print("!" * 50)
        print(f"CRITICAL GEMINI VISION ERROR: {e}")
        traceback.print_exc()
        print("!" * 50)
        return {"error": str(e)}
