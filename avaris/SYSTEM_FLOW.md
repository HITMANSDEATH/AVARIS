# AVARIS System Flow Diagram

## Complete Food Analysis Pipeline - Two-Stage Gemini AI

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ESP32-CAM / User Upload                      │
│                              (Food Image)                            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (/upload-food-image)              │
│                         Save image to disk                           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STAGE 1: GEMINI VISION API - IMAGE ANALYSIS             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  backend/ai_engine/gemini_vision.py                           │  │
│  │  • Model: Gemini 2.0 Flash (Vision)                           │  │
│  │  • Input: Food image file                                     │  │
│  │  • Analysis:                                                  │  │
│  │    - Identify main food item(s)                               │  │
│  │    - Extract visible ingredients                              │  │
│  │    - Infer hidden/common ingredients                          │  │
│  │    - Calculate confidence score                               │  │
│  │  • Output: {                                                  │  │
│  │      "food_item": "Margherita Pizza",                         │  │
│  │      "ingredients": ["wheat flour", "mozzarella cheese",      │  │
│  │                      "tomato sauce", "olive oil", "basil"],   │  │
│  │      "confidence": 0.95                                       │  │
│  │    }                                                          │  │
│  │  • Processing: ~2-4 seconds (API call)                        │  │
│  │  • Accuracy: High (understands food context)                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    LOCAL ALLERGEN CHECKING                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  ml/allergen_checker.py                                       │  │
│  │  • Allergen DB: database/allergen_db.json                     │  │
│  │  • Input: ["wheat flour", "mozzarella cheese", ...]          │  │
│  │  • Match: wheat → gluten, cheese → dairy                      │  │
│  │  • Output: (["gluten", "dairy"], "HIGH")                      │  │
│  │  • Risk Logic:                                                │  │
│  │    - 0 allergens → LOW                                        │  │
│  │    - 1 allergen  → MEDIUM                                     │  │
│  │    - 2+ allergens → HIGH                                      │  │
│  │  • Processing: <0.01 seconds (local)                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│           STAGE 2: GEMINI TEXT API - EXPLANATION GENERATION          │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  backend/ai_engine/text_analyzer.py                           │  │
│  │  backend/ai_engine/reasoning.py                               │  │
│  │  • Model: Gemini 2.0 Flash (Text)                             │  │
│  │  • Input: Food item, ingredients, allergens, risk level       │  │
│  │  • Prompt: "Analyze this food report..."                      │  │
│  │  • Output: "HIGH RISK: This Margherita pizza contains         │  │
│  │            gluten (from wheat flour) and dairy (from          │  │
│  │            mozzarella cheese). If you have celiac disease     │  │
│  │            or lactose intolerance, avoid this food..."        │  │
│  │  • Processing: ~1-2 seconds (API call)                        │  │
│  │  • Fallback: Rule-based explanation if API unavailable        │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE LOGGING                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  backend/database/models.py (FoodAnalysisLog)                 │  │
│  │  • Store complete analysis result                             │  │
│  │  • Timestamp, image path, all detected data                   │  │
│  │  • Queryable history for user                                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    API RESPONSE TO FRONTEND                          │
│  {                                                                   │
│    "food_item": "Margherita Pizza",                                  │
│    "ingredients": ["wheat flour", "mozzarella cheese", "tomato      │
│                    sauce", "olive oil", "basil"],                    │
│    "detected_allergens": ["gluten", "dairy"],                        │
│    "risk_level": "HIGH",                                             │
│    "confidence": 0.95,                                               │
│    "ai_explanation": "HIGH RISK: This pizza contains...",            │
│    "image_url": "/uploads/food_images/food_20260313_120000.jpg"     │
│  }                                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND DASHBOARD                                │
│  • Display food item with image                                     │
│  • Show comprehensive ingredient list                               │
│  • Highlight detected allergens                                     │
│  • Display risk level with color coding                             │
│  • Show AI-generated explanation                                    │
│  • Alert user if HIGH risk                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Environmental Monitoring Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ESP32 Sensor (Temperature, Humidity, Dust)        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (/sensor-data)                    │
│                         Store sensor reading                         │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ML MODELS (Scikit-learn)                          │
│  • Anomaly Detection (Isolation Forest)                             │
│  • Risk Prediction (Classification)                                 │
│  • Forecast (Regression)                                            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    GEMINI TEXT API - EXPLANATION                     │
│  • Generate anomaly explanations                                    │
│  • Explain risk factors                                             │
│  • Provide recommendations                                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DATABASE & DASHBOARD                              │
│  • Log events and predictions                                       │
│  • Display real-time monitoring                                     │
│  • Show AI explanations                                             │
└─────────────────────────────────────────────────────────────────────┘
```

## Two-Stage Gemini AI Architecture

### STAGE 1: Vision Analysis (Gemini Vision API)
```
┌──────────────────────────────────────┐
│  Image Analysis                      │
│  • Gemini 2.0 Flash (Vision)         │
│  • Food identification               │
│  • Ingredient extraction             │
│  • Confidence scoring                │
│  • ~2-4 seconds                      │
│  • High accuracy                     │
└──────────────────────────────────────┘
```

### LOCAL PROCESSING (Fast, Private)
```
┌──────────────────────────────────────┐
│  Allergen Checking                   │
│  • Pattern matching                  │
│  • Risk calculation                  │
│  • <0.01 seconds                     │
│  • Local database                    │
└──────────────────────────────────────┘
```

### STAGE 2: Text Analysis (Gemini Text API)
```
┌──────────────────────────────────────┐
│  Explanation Generation              │
│  • Gemini 2.0 Flash (Text)           │
│  • Natural language explanations     │
│  • Contextual reasoning              │
│  • Safety recommendations            │
│  • ~1-2 seconds                      │
│  • Fallback if unavailable           │
└──────────────────────────────────────┘
```

## Performance Characteristics

| Component              | Processing Time | Location | Accuracy | Cost      |
|------------------------|-----------------|----------|----------|-----------|
| Gemini Vision API      | 2-4 sec         | Cloud    | High     | Per call  |
| Allergen Checking      | <0.01 sec       | Local    | High     | Free      |
| Gemini Text API        | 1-2 sec         | Cloud    | High     | Per call  |
| **Total Pipeline**     | **~3-6 sec**    | Hybrid   | High     | Low       |

## Data Privacy & Security

```
┌─────────────────────────────────────────────────────────────────────┐
│  SENT TO GEMINI VISION API (Stage 1)                                │
│  • Food image (for analysis only)                                   │
│  • Processed by Google's secure infrastructure                      │
│  • Not stored permanently by default                                │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  PROCESSED LOCALLY (Private)                                        │
│  • Allergen database matching                                       │
│  • Risk level calculation                                           │
│  • Database logging                                                 │
│  • User upload history                                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  SENT TO GEMINI TEXT API (Stage 2)                                  │
│  • Food item name: "Margherita Pizza"                               │
│  • Ingredients list: ["wheat flour", "cheese"]                      │
│  • Allergens: ["gluten", "dairy"]                                   │
│  • Risk level: "HIGH"                                               │
│  • NO images, NO personal identifiable information                  │
└─────────────────────────────────────────────────────────────────────┘
```

## Startup Sequence

```
1. FastAPI Application Start
   ↓
2. Initialize Database
   ↓
3. Initialize Gemini Vision Analyzer
   ↓
4. Initialize Gemini Text Analyzer
   ↓
5. Initialize Allergen Checker (load local database)
   ↓
6. Server Ready (http://localhost:8000)
   ↓
   Total startup time: ~1-2 seconds
```

## Error Handling & Fallbacks

```
Gemini Vision API Fails
   ↓
Return error to user
(Core functionality - no fallback)

Gemini Text API Unavailable
   ↓
Use rule-based explanations
(System continues with basic explanations)

Allergen DB Missing
   ↓
Create default allergen DB
(Auto-recovery)
```

## Advantages of Two-Stage Gemini System

### Why Gemini Vision > Local Models?
✓ Understands thousands of food types (not limited to 101)
✓ Extracts ingredients directly (no separate inference needed)
✓ Context-aware (understands food composition)
✓ Identifies hidden ingredients
✓ Continuously improving (Google updates)
✓ No large model downloads
✓ Better accuracy for complex dishes

### Why Two Stages?
✓ Separation of concerns (vision vs text)
✓ Each API optimized for its task
✓ Can fallback text analysis independently
✓ Better error handling
✓ More maintainable code