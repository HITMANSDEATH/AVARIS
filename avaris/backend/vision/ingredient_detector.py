"""
Gemini Vision-based Food Detection
Uses Gemini Vision API to analyze food images and extract ingredients
"""

import logging
from backend.ai_engine.gemini_vision import analyze_food_image

logger = logging.getLogger(__name__)

def detect_ingredients(image_path: str) -> dict:
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
    try:
        logger.info(f"Analyzing food image with Gemini Vision: {image_path}")
        
        # Use Gemini Vision to analyze the image
        result = analyze_food_image(image_path)
        
        if "error" in result:
            logger.error(f"Gemini Vision analysis failed: {result['error']}")
            return result
        
        food_item = result.get("food_item", "Unknown")
        ingredients = result.get("ingredients", [])
        confidence = result.get("confidence", 0.0)
        
        logger.info(f"Gemini Vision detected: {food_item}")
        logger.info(f"Ingredients found: {ingredients}")
        logger.info(f"Confidence: {confidence}")
        
        return {
            "food_item": food_item,
            "ingredients": ingredients,
            "confidence": confidence
        }
        
    except Exception as e:
        logger.error(f"Error in detect_ingredients: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
