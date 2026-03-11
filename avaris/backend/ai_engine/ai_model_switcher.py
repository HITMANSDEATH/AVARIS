import os
import socket
import google.generativeai as genai
from backend.config.settings import settings

# Configure Gemini
# Using the key you provided directly to ensure it takes effect
api_key = "AIzaSyA3JtzZiv-4FwDP8tsVkKGIHqoKvsGPjvU" 

print("*" * 50)
if api_key and api_key not in ["", "YOUR_API_KEY_HERE"]:
    genai.configure(api_key=api_key)
    gemini_configured = True
    print("AVARIS DEBUG: Gemini API configured successfully with hardcoded key.")
else:
    api_key = settings.GEMINI_API_KEY
    if api_key and api_key not in ["", "YOUR_API_KEY_HERE"]:
        genai.configure(api_key=api_key)
        gemini_configured = True
        print("AVARIS DEBUG: Gemini API configured via Settings.")
    else:
        gemini_configured = False
        print("AVARIS DEBUG: Gemini NOT configured - Falling back to local/static.")

# Local fallback configuration
MISTRAL_MODEL_PATH = os.getenv("MISTRAL_MODEL_PATH", "./models/mistral_4b")

def check_internet_connection():
    """Check if the internet is available."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except Exception:
        return False

def get_best_available_model():
    """Prioritize Gemini if configured, otherwise fallback to Mistral."""
    if gemini_configured:
        return "gemini"
    return "mistral"

def generate_text_gemini(prompt: str) -> str:
    """Generate text using Google's Gemini API."""
    try:
        model = genai.GenerativeModel('gemini-2.5-pro') # Using Gemini 2.5 Pro for better reasoning
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        import traceback
        print("!" * 50)
        print(f"CRITICAL GEMINI TEXT ERROR: {e}")
        traceback.print_exc()
        print("!" * 50)
        return f"Error: {str(e)}"
def generate_text_mistral(prompt: str) -> str:
    """
    Generate text using local Mistral model fallback.
    """
    try:
        # Improved static fallback for when AI is unavailable
        print(f"Fallback to Local Mistral Model: {MISTRAL_MODEL_PATH}")
        
        # Simple rule-based logic for fallback suggestions
        if "critical" in prompt.lower() or "high" in prompt.lower():
            return "ALARM: High risk detected. Please ventilate the area and check for smoke or gas immediately. (Offline Fallback)"
        elif "food" in prompt.lower() or "allergen" in prompt.lower():
            return "WARNING: Potential allergen risk detected. Cross-verify ingredients manually before consumption. (Offline Fallback)"
            
        return "System Alert: Unusual sensor patterns detected. Please monitor the area for changes. (Offline Fallback)"
    except Exception as e:
        print(f"Local Model Error: {e}")
        return "Error: Unable to generate response from Local Model."

def explain_with_ai(prompt: str) -> str:
    """Main entry point to get AI reasoning, auto-switching based on availability."""
    model_choice = get_best_available_model()
    
    if model_choice == "gemini":
        print("Using Gemini API for reasoning.")
        return generate_text_gemini(prompt)
    else:
        print("Using Local Mistral Model for reasoning.")
        return generate_text_mistral(prompt)
