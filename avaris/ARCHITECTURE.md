# AVARIS Architecture - Two-Stage Gemini AI System

## Overview
AVARIS (AI-based Vision and Allergen Risk Identification System) uses a two-stage Gemini AI approach:
- **Stage 1: Gemini Vision API** - Analyzes food images and extracts ingredients
- **Stage 2: Gemini Text API** - Analyzes ingredients and provides intelligent explanations

## Architecture Flow

```
ESP32-CAM Image Upload
         ↓
Backend API (/upload-food-image)
         ↓
STAGE 1: Gemini Vision API
         ↓
Food Item + Ingredients Detection
         ↓
Local Allergen Matching
         ↓
Risk Classification (LOW/MEDIUM/HIGH)
         ↓
STAGE 2: Gemini Text API
         ↓
Intelligent Explanation & Recommendations
         ↓
Database Logging
         ↓
Frontend Dashboard Alert
```

## Key Components

### 1. Gemini Vision API (`backend/ai_engine/gemini_vision.py`)
- **Stage 1**: Image analysis and ingredient extraction
- Model: Gemini 2.0 Flash with vision capabilities
- Analyzes food images to identify:
  - Main food item(s)
  - Visible ingredients
  - Hidden/common ingredients
  - Confidence score
- Returns comprehensive ingredient list
- **Smart and accurate** - understands food context

### 2. Allergen Checking (`ml/allergen_checker.py`)
- Matches extracted ingredients against allergen database
- Database: `database/allergen_db.json`
- Calculates risk levels:
  - 0 allergens → LOW
  - 1 allergen → MEDIUM  
  - 2+ allergens → HIGH
- **Local processing** - fast and private

### 3. Gemini Text API (`backend/ai_engine/text_analyzer.py`)
- **Stage 2**: Text-based analysis and explanations
- Model: Gemini 2.0 Flash for text generation
- Handles:
  - Food allergen safety explanations
  - Environmental anomaly explanations
  - Risk level reasoning
  - Personalized recommendations
- Graceful fallback to rule-based explanations

### 4. Reasoning Module (`backend/ai_engine/reasoning.py`)
- Orchestrates Gemini Text API calls
- Provides context-aware explanations for:
  - Food allergen risks
  - Sensor anomalies
  - Environmental risks
- Includes fallback logic when API unavailable

### 5. Vision Module (`backend/vision/ingredient_detector.py`)
- Wrapper for Gemini Vision API
- Handles image loading and API communication
- Returns structured food analysis results

## Two-Stage Gemini AI Benefits

### Stage 1: Gemini Vision API
✓ Highly accurate food recognition
✓ Comprehensive ingredient extraction
✓ Understands food context and composition
✓ Identifies hidden ingredients
✓ Confidence scoring
✓ Handles complex dishes

### Stage 2: Gemini Text API
✓ Intelligent, contextual explanations
✓ Natural language generation
✓ Personalized safety recommendations
✓ Adaptive reasoning
✓ Better user experience

## Why Two Stages?

**Separation of Concerns:**
- Vision API specializes in image understanding
- Text API specializes in explanation generation
- Each API optimized for its specific task

**Better Results:**
- Vision API extracts detailed ingredients
- Text API provides context-aware explanations
- Combined: comprehensive food safety analysis

## Dependencies

### Required Libraries
```
google-generativeai  # For both vision and text analysis
pillow              # Image processing
opencv-python       # Computer vision utilities
fastapi             # Web framework
uvicorn             # ASGI server
pandas              # Data processing
numpy               # Numerical operations
scikit-learn        # ML models (environmental monitoring)
sqlalchemy          # Database ORM
python-dotenv       # Environment variables
```

### Removed Dependencies
- `torch` - No longer needed (removed local Vision Transformer)
- `torchvision` - No longer needed
- `transformers` - No longer needed

## API Response Format

The `/upload-food-image` endpoint returns:
```json
{
  "food_item": "Margherita Pizza",
  "ingredients": ["wheat flour", "mozzarella cheese", "tomato sauce", "olive oil", "basil", "yeast"],
  "detected_allergens": ["gluten", "dairy"],
  "risk_level": "HIGH",
  "confidence": 0.95,
  "ai_explanation": "HIGH RISK: This Margherita pizza contains gluten (from wheat flour) and dairy (from mozzarella cheese). If you have celiac disease or lactose intolerance, avoid this food. Seek medical attention if consumed and symptoms appear.",
  "image_url": "/uploads/food_images/food_20260313_120000.jpg"
}
```

## Data Flow

### Complete Pipeline
```
Image → Gemini Vision API → Food + Ingredients → 
Local Allergen Check → Risk Level → 
Gemini Text API → Explanation → Database → Dashboard
```

### Stage 1: Vision Analysis
```
Input: Food image (JPEG/PNG)
   ↓
Gemini Vision API
   ↓
Output: {
  "food_item": "Pizza",
  "ingredients": ["wheat", "cheese", "tomato"],
  "confidence": 0.95
}
```

### Stage 2: Text Analysis
```
Input: Food item, ingredients, allergens, risk level
   ↓
Gemini Text API
   ↓
Output: "HIGH RISK: This pizza contains gluten and dairy..."
```

## Performance Characteristics

| Component              | Processing Time | Location | Accuracy |
|------------------------|-----------------|----------|----------|
| Gemini Vision API      | 2-4 sec         | Cloud    | High     |
| Allergen Checking      | <0.01 sec       | Local    | High     |
| Gemini Text API        | 1-2 sec         | Cloud    | High     |
| **Total Pipeline**     | **~3-6 sec**    | Hybrid   | High     |

## Configuration

### Gemini API Key
Set in `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

Or use hardcoded key in development (already configured in code).

## Testing

Run the test script to verify both stages:
```bash
cd avaris
python test_vision_pipeline.py
```

This will test:
1. Gemini Vision API availability
2. Image analysis and ingredient extraction
3. Allergen checking
4. Gemini Text API explanation generation

## Benefits of Two-Stage Gemini System

1. **High Accuracy**: Gemini Vision understands food context better than generic models
2. **Comprehensive**: Extracts both visible and hidden ingredients
3. **Intelligent**: Context-aware explanations tailored to the situation
4. **Consistent**: Single AI provider for both stages
5. **Reliable**: Proven Google AI technology
6. **Scalable**: Cloud-based, handles any load
7. **Maintained**: Google keeps models updated

## Comparison with Previous Approach

### Local Vision Transformer (Removed)
- ❌ Limited to Food101 dataset (101 food types)
- ❌ Generic food labels only
- ❌ No ingredient extraction
- ❌ Required separate inference step
- ❌ Large model download (~500MB)

### Gemini Vision API (Current)
- ✅ Understands thousands of food types
- ✅ Extracts detailed ingredients directly
- ✅ Context-aware analysis
- ✅ No model downloads needed
- ✅ Continuously improving

## Future Enhancements

1. **Batch Processing**: Analyze multiple images simultaneously
2. **Nutritional Analysis**: Add calorie and nutrient information
3. **Multi-language**: Support explanations in multiple languages
4. **Voice Output**: Convert text explanations to speech
5. **Custom Allergen Profiles**: User-specific allergen databases
6. **Recipe Suggestions**: Safe alternative recipes