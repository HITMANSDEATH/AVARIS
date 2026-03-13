#!/usr/bin/env python3
"""
Test script for the AVARIS two-stage Gemini AI pipeline
Tests the Gemini Vision API for image analysis and Gemini Text API for explanations
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.ai_engine.gemini_vision import analyze_food_image
from ml.allergen_checker import check_ingredients_for_allergens
from backend.ai_engine.reasoning import explain_food_risk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_pipeline():
    """Test the complete two-stage Gemini AI pipeline"""
    
    # Check if we have any test images
    test_image_dir = "uploads/food_images"
    if not os.path.exists(test_image_dir):
        logger.warning(f"Test image directory {test_image_dir} not found")
        return
    
    # Get the first available image
    image_files = [f for f in os.listdir(test_image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not image_files:
        logger.warning("No test images found in uploads/food_images/")
        return
    
    test_image = os.path.join(test_image_dir, image_files[0])
    logger.info(f"Testing with image: {test_image}")
    
    try:
        # Stage 1: Gemini Vision - Analyze image and extract ingredients
        logger.info("\n" + "="*60)
        logger.info("STAGE 1: GEMINI VISION API - Image Analysis")
        logger.info("="*60)
        
        vision_result = analyze_food_image(test_image)
        
        if "error" in vision_result:
            logger.error(f"Gemini Vision failed: {vision_result['error']}")
            return
        
        food_item = vision_result["food_item"]
        ingredients = vision_result["ingredients"]
        confidence = vision_result["confidence"]
        
        logger.info(f"✓ Food Item: {food_item}")
        logger.info(f"✓ Confidence: {confidence}")
        logger.info(f"✓ Ingredients: {ingredients}")
        
        # Stage 2: Allergen Checking (Local)
        logger.info("\n" + "="*60)
        logger.info("STAGE 2: LOCAL ALLERGEN CHECKING")
        logger.info("="*60)
        
        detected_allergens, risk_level = check_ingredients_for_allergens(ingredients)
        logger.info(f"✓ Detected Allergens: {detected_allergens}")
        logger.info(f"✓ Risk Level: {risk_level}")
        
        # Stage 3: Gemini Text - Generate explanation
        logger.info("\n" + "="*60)
        logger.info("STAGE 3: GEMINI TEXT API - Explanation Generation")
        logger.info("="*60)
        
        explanation = explain_food_risk(food_item, ingredients, detected_allergens, risk_level)
        logger.info(f"✓ AI Explanation:\n{explanation}")
        
        # Final result
        logger.info("\n" + "="*60)
        logger.info("TWO-STAGE GEMINI PIPELINE TEST COMPLETE")
        logger.info("="*60)
        logger.info(f"Food Item: {food_item}")
        logger.info(f"Confidence: {confidence}")
        logger.info(f"Ingredients: {ingredients}")
        logger.info(f"Detected Allergens: {detected_allergens}")
        logger.info(f"Risk Level: {risk_level}")
        logger.info(f"Explanation: {explanation[:100]}...")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()

def test_gemini_availability():
    """Test if Gemini APIs are available"""
    logger.info("Testing Gemini API availability...")
    
    try:
        from backend.ai_engine.gemini_vision import get_vision_analyzer
        from backend.ai_engine.text_analyzer import get_text_analyzer
        
        vision_analyzer = get_vision_analyzer()
        text_analyzer = get_text_analyzer()
        
        if vision_analyzer.is_available():
            logger.info("✓ Gemini Vision API is available")
        else:
            logger.error("✗ Gemini Vision API is NOT available")
            return False
        
        if text_analyzer.is_available():
            logger.info("✓ Gemini Text API is available")
        else:
            logger.warning("⚠ Gemini Text API is NOT available (will use fallback)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Failed to check Gemini availability: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting AVARIS Two-Stage Gemini AI Pipeline Test")
    logger.info("="*60)
    
    # Test 1: API availability
    if not test_gemini_availability():
        logger.error("\nGemini APIs not available. Please check:")
        logger.error("1. GEMINI_API_KEY is set in .env file")
        logger.error("2. API key is valid and active")
        logger.error("3. Internet connection is working")
        sys.exit(1)
    
    logger.info("\n")
    
    # Test 2: Full pipeline
    test_gemini_pipeline()
    
    logger.info("\nTest complete!")