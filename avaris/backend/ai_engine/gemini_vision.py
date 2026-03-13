"""
Gemini Vision API Module
Stage 1: Analyzes food images and extracts ingredients
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image
import json
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GeminiVisionAnalyzer:
    """Gemini Vision API for food image analysis"""
    
    def __init__(self):
        self.model = None
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure Gemini Vision API"""
        api_key = os.getenv("GEMINIV_API_KEY")
        
        if not api_key or api_key.strip() == "":
            logger.warning("GEMINIV_API_KEY not found in environment variables")
            self.model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini vision analyzer configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini Vision: {e}")
            self.model = None
    
    def analyze_food_image(self, image_path: str) -> dict:
        """
        Analyze food image using Gemini Vision API
        
        Args:
            image_path (str): Path to the food image
            
        Returns:
            dict: {
                "food_item": str,
                "ingredients": list,
                "confidence": float
            }
        """
        if not self.model:
            logger.error("Gemini Vision not configured")
            return {"error": "Gemini Vision API not configured. Please set GEMINI_API_KEY."}
        
        try:
            # Load image
            img = Image.open(image_path)
            
            # Create detailed prompt for food analysis
            prompt = """
            Analyze this food image carefully and provide detailed information.

            Your task:
            1. Identify the main food item(s) in the image
            2. List ALL visible ingredients you can see
            3. List common hidden ingredients typically found in this type of food
            4. Provide a confidence score (0.0 to 1.0) for your identification

            IMPORTANT: Be thorough with ingredients. Include:
            - Base ingredients (flour, rice, meat, etc.)
            - Dairy products (milk, cheese, butter, cream)
            - Common allergens (nuts, eggs, soy, wheat, fish, shellfish)
            - Seasonings and additives if visible
            - Cooking oils or fats

            Return your response in this EXACT JSON format:
            {
                "food_item": "name of the food",
                "ingredients": ["ingredient1", "ingredient2", "ingredient3"],
                "confidence": 0.95
            }

            Be specific and comprehensive with ingredients. If you see cheese, specify it. If you see bread, include wheat/flour.
            """
            
            # Generate content with image
            response = self.model.generate_content([prompt, img])
            
            # Parse response
            text_response = response.text.strip()
            
            # Clean up markdown formatting if present
            if text_response.startswith("```json"):
                text_response = text_response.split("```json")[1].split("```")[0].strip()
            elif text_response.startswith("```"):
                text_response = text_response.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            result = json.loads(text_response)
            
            logger.info(f"Gemini Vision Analysis: {result['food_item']} with {len(result.get('ingredients', []))} ingredients")
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini Vision response as JSON: {e}")
            logger.error(f"Response text: {text_response}")
            return {
                "error": "Failed to parse vision analysis response",
                "raw_response": text_response
            }
        except Exception as e:
            logger.error(f"Error analyzing food image with Gemini Vision: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def is_available(self) -> bool:
        """Check if Gemini Vision is available"""
        return self.model is not None

# Global vision analyzer instance
_vision_analyzer = None

def get_vision_analyzer() -> GeminiVisionAnalyzer:
    """Get the global vision analyzer instance"""
    global _vision_analyzer
    if _vision_analyzer is None:
        _vision_analyzer = GeminiVisionAnalyzer()
    return _vision_analyzer

def analyze_food_image(image_path: str) -> dict:
    """
    Convenience function to analyze food image
    
    Args:
        image_path (str): Path to the food image
        
    Returns:
        dict: Analysis result with food_item, ingredients, and confidence
    """
    analyzer = get_vision_analyzer()
    return analyzer.analyze_food_image(image_path)

def analyze_food_image_gemini(image_path: str) -> dict:
    """
    Alias for analyze_food_image for backward compatibility
    
    Args:
        image_path (str): Path to the food image
        
    Returns:
        dict: Analysis result with food_item, ingredients, and confidence
    """
    return analyze_food_image(image_path)