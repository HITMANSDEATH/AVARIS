# AVARIS Quick Start Guide - Two-Stage Gemini AI

## Installation

### 1. Install Dependencies
```bash
cd avaris
pip install -r requirements.txt
```

This will install:
- Google Generative AI (Gemini API for vision and text)
- FastAPI and other backend dependencies
- Image processing libraries (Pillow, OpenCV)
- ML libraries for environmental monitoring

### 2. Configure Gemini API Key
Create or update `.env` file:
```bash
GEMINI_API_KEY=your_api_key_here
```

**Note:** A hardcoded key is already configured in the code for development purposes.

### 3. Initialize Database
```bash
python -c "from backend.database.init_db import init_db; init_db()"
```

## Running the System

### Start Backend Server
```bash
python main.py
```

The server will:
1. Initialize the database
2. Initialize Gemini Vision analyzer (Stage 1)
3. Initialize Gemini Text analyzer (Stage 2)
4. Initialize Allergen checker
5. Start API server on `http://localhost:8000`

### Test the Two-Stage Gemini Pipeline
```bash
python test_vision_pipeline.py
```

## Architecture Overview

### Stage 1: Gemini Vision API (Image Analysis)
```python
# backend/ai_engine/gemini_vision.py
from backend.ai_engine.gemini_vision import analyze_food_image

result = analyze_food_image("path/to/image.jpg")
# Returns: {
#   "food_item": "Margherita Pizza",
#   "ingredients": ["wheat flour", "mozzarella cheese", "tomato sauce"],
#   "confidence": 0.95
# }
```

### Local Allergen Checking
```python
# ml/allergen_checker.py
from ml.allergen_checker import check_ingredients_for_allergens

allergens, risk = check_ingredients_for_allergens(["wheat flour", "cheese"])
# Returns: (["gluten", "dairy"], "HIGH")
```

### Stage 2: Gemini Text API (Explanation Generation)
```python
# backend/ai_engine/text_analyzer.py
from backend.ai_engine.text_analyzer import generate_ai_text

explanation = generate_ai_text("Explain why gluten is an allergen")
# Returns: AI-generated explanation
```

## API Endpoints

### Upload Food Image
```bash
POST /api/upload-food-image
Content-Type: multipart/form-data

# Response:
{
  "food_item": "Margherita Pizza",
  "ingredients": ["wheat flour", "mozzarella cheese", "tomato sauce", "olive oil", "basil"],
  "detected_allergens": ["gluten", "dairy"],
  "risk_level": "HIGH",
  "confidence": 0.95,
  "ai_explanation": "HIGH RISK: This pizza contains gluten and dairy...",
  "image_url": "/uploads/food_images/food_20260313_120000.jpg"
}
```

### Get Latest Food Analysis
```bash
GET /api/latest-food-analysis

# Response: Same as upload response
```

### Sensor Data (Environmental Monitoring)
```bash
POST /api/sensor-data
Content-Type: application/json

{
  "temperature": 25.5,
  "humidity": 60.0,
  "dust": 35.2
}
```

## File Structure

```
avaris/
├── backend/
│   ├── ai_engine/
│   │   ├── gemini_vision.py         # NEW: Stage 1 - Image analysis
│   │   ├── text_analyzer.py         # Stage 2 - Text generation
│   │   └── reasoning.py             # Orchestrates explanations
│   ├── vision/
│   │   └── ingredient_detector.py   # UPDATED: Uses Gemini Vision
│   ├── api/
│   │   └── routes.py                # API endpoints
│   └── database/
│
├── ml/
│   └── allergen_checker.py          # Local allergen matching
│
├── database/
│   └── allergen_db.json             # Allergen → Keywords mapping
│
├── uploads/food_images/             # Uploaded food images
├── main.py                          # UPDATED: Initializes Gemini APIs
└── test_vision_pipeline.py          # UPDATED: Tests two-stage pipeline
```

## Common Tasks

### Add New Allergen
Edit `database/allergen_db.json`:
```json
{
  "shellfish": ["shrimp", "crab", "lobster"],
  "your_allergen": ["keyword1", "keyword2"]
}
```

### Customize Risk Levels
Edit `ml/allergen_checker.py`:
```python
def calculate_risk_level(self, detected_allergens: list) -> str:
    count = len(detected_allergens)
    if count == 0:
        return "LOW"
    elif count == 1:
        return "MEDIUM"
    else:  # 2+
        return "HIGH"
```

## Troubleshooting

### Gemini API Not Working
- Check API key in `.env`
- Verify API key is valid and active
- Check internet connection
- System will use fallback explanations for text analysis
- Vision analysis requires working API (no fallback)

### Low Confidence Scores
- Gemini Vision is highly accurate
- Low confidence may indicate:
  - Blurry or poor quality image
  - Unusual or rare food items
  - Multiple food items in one image

### Slow Response Times
- First API call may be slower (cold start)
- Subsequent calls are faster
- Total pipeline: ~3-6 seconds
  - Stage 1 (Vision): 2-4 seconds
  - Stage 2 (Text): 1-2 seconds

## Performance Tips

1. **Keep server running**: Model stays loaded in memory
2. **Use GPU if available**: PyTorch will automatically use CUDA
3. **Batch processing**: Process multiple images in sequence
4. **Cache results**: Store analysis results in database

## Development

### Run in Development Mode
```bash
python main.py
# Server auto-reloads on code changes
```

### Run Tests
```bash
python test_vision_pipeline.py
```

### Check Logs
```bash
# Logs show:
# - Model loading status
# - API requests
# - Classification results
# - Errors and warnings
```

## Production Deployment

### Environment Variables
```bash
GEMINI_API_KEY=your_production_key
DATABASE_URL=your_database_url
```

### Optimize for Production
1. Set `reload=False` in `main.py`
2. Use production WSGI server (gunicorn)
3. Enable HTTPS
4. Set proper CORS origins
5. Add rate limiting
6. Monitor API usage

## Resources

- Vision Transformer Model: https://huggingface.co/nateraw/vit-base-food101
- Gemini API Docs: https://ai.google.dev/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- PyTorch Docs: https://pytorch.org/docs

## Support

For issues:
1. Check `ARCHITECTURE.md` for system design
2. Check `MIGRATION_SUMMARY.md` for changes
3. Review logs for error messages
4. Test with `test_vision_pipeline.py`