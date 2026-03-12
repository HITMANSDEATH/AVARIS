# Design Document: System Performance Optimization

## Overview

This design addresses comprehensive performance optimization for the Avaris environmental monitoring and food allergen detection system. The current system uses Gemini Vision API for image analysis, scikit-learn models for environmental risk prediction, and a FastAPI backend with SQLite database. The optimization focuses on four key areas: (1) replacing Gemini Vision with a more efficient open-source vision model, (2) implementing caching and async processing for API performance, (3) optimizing ML inference pipelines with model quantization and batching, and (4) upgrading database architecture for scalability. The design combines architectural improvements with algorithmic optimizations to achieve significant performance gains while maintaining accuracy.

## Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        React[React Frontend]
    end
    
    subgraph "API Gateway Layer"
        FastAPI[FastAPI Server]
        Cache[Redis Cache]
        Queue[Task Queue - Celery]
    end
    
    subgraph "Processing Layer"
        VisionWorker[Vision Processing Worker]
        MLWorker[ML Inference Worker]
        DataWorker[Data Processing Worker]
    end
    
    subgraph "Model Layer"
        VisionModel[CLIP/BLIP-2 Vision Model]
        RiskModel[Optimized Risk Model]
        AnomalyModel[Optimized Anomaly Model]
        ForecastModel[Optimized Forecast Model]
    end
    
    subgraph "Storage Layer"
        PostgreSQL[(PostgreSQL)]
        ModelCache[Model Cache]
        ImageStore[Image Storage]
    end
    
    React -->|HTTP/WebSocket| FastAPI
    FastAPI -->|Check Cache| Cache
    FastAPI -->|Enqueue Tasks| Queue
    Queue -->|Distribute| VisionWorker
    Queue -->|Distribute| MLWorker
    Queue -->|Distribute| DataWorker
    VisionWorker -->|Load Model| VisionModel
    MLWorker -->|Load Models| RiskModel
    MLWorker -->|Load Models| AnomalyModel
    MLWorker -->|Load Models| ForecastModel
    VisionWorker -->|Store Results| PostgreSQL
    MLWorker -->|Store Results| PostgreSQL
    DataWorker -->|Query/Store| PostgreSQL
    VisionModel -->|Cache Embeddings| ModelCache
    VisionWorker -->|Store Images| ImageStore
```

## Main Algorithm/Workflow

```mermaid
sequenceDiagram
    participant Client as React Client
    participant API as FastAPI Server
    participant Cache as Redis Cache
    participant Queue as Task Queue
    participant Worker as Processing Worker
    participant Model as ML Model
    participant DB as PostgreSQL
    
    Client->>API: Upload Food Image
    API->>Cache: Check if image hash exists
    alt Cache Hit
        Cache-->>API: Return cached result
        API-->>Client: Return result (< 50ms)
    else Cache Miss
        API->>Queue: Enqueue vision task
        API-->>Client: Return task_id (async)
        Queue->>Worker: Dispatch task
        Worker->>Model: Load optimized model
        Model-->>Worker: Inference result
        Worker->>Cache: Store result
        Worker->>DB: Log analysis
        Worker-->>Client: WebSocket notification
    end
    
    Client->>API: Request sensor prediction
    API->>Cache: Check recent prediction
    alt Cache Hit
        Cache-->>API: Return cached prediction
    else Cache Miss
        API->>Worker: Batch inference request
        Worker->>Model: Batch predict (10 samples)
        Model-->>Worker: Predictions
        Worker->>Cache: Store predictions
        Worker->>DB: Store predictions
    end
    Worker-->>API: Results
    API-->>Client: Return predictions
```

## Components and Interfaces

### Component 1: Vision Model Service

**Purpose**: Replace Gemini Vision API with open-source vision-language model for food ingredient detection

**Interface**:
```python
from typing import List, Dict, Optional
from PIL import Image

class VisionModelService:
    def analyze_food_image(self, image: Image, use_cache: bool = True) -> Dict:
        """Analyze food image and extract ingredients using CLIP/BLIP-2"""
        pass
    
    def get_image_embeddings(self, image: Image) -> List[float]:
        """Generate image embeddings for similarity search"""
        pass
    
    def batch_analyze(self, images: List[Image]) -> List[Dict]:
        """Batch process multiple images for efficiency"""
        pass
    
    def warm_up_model(self) -> None:
        """Pre-load model into memory for faster inference"""
        pass

class ModelConfig:
    model_name: str  # "Salesforce/blip2-opt-2.7b" or "openai/clip-vit-large-patch14"
    device: str  # "cuda" or "cpu"
    quantization: str  # "int8", "fp16", or "fp32"
    max_batch_size: int
    cache_embeddings: bool
```

**Responsibilities**:
- Load and manage vision-language model (BLIP-2 or CLIP)
- Process food images to extract ingredients and descriptions
- Generate embeddings for similarity-based caching
- Support batch processing for multiple images
- Implement model quantization for memory efficiency

### Component 2: Caching Layer

**Purpose**: Implement Redis-based caching for API responses and model predictions

**Interface**:
```python
from typing import Any, Optional
from datetime import timedelta

class CacheService:
    def get(self, key: str) -> Optional[Any]:
        """Retrieve cached value by key"""
        pass
    
    def set(self, key: str, value: Any, ttl: timedelta) -> bool:
        """Store value with time-to-live"""
        pass
    
    def get_or_compute(self, key: str, compute_fn: callable, ttl: timedelta) -> Any:
        """Get from cache or compute and store"""
        pass
    
    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern"""
        pass
    
    def get_image_hash(self, image_path: str) -> str:
        """Generate perceptual hash for image deduplication"""
        pass

class CacheStrategy:
    sensor_data_ttl: timedelta  # 30 seconds
    risk_prediction_ttl: timedelta  # 5 minutes
    food_analysis_ttl: timedelta  # 24 hours
    model_embedding_ttl: timedelta  # 7 days
```

**Responsibilities**:
- Manage Redis connection pool
- Implement cache-aside pattern for API responses
- Generate perceptual hashes for image deduplication
- Handle cache invalidation strategies
- Monitor cache hit rates and performance

### Component 3: Async Task Queue

**Purpose**: Implement Celery-based task queue for long-running operations

**Interface**:
```python
from celery import Celery
from typing import Dict, Any

class TaskQueue:
    def enqueue_vision_analysis(self, image_path: str, user_id: str) -> str:
        """Enqueue food image analysis task"""
        pass
    
    def enqueue_batch_prediction(self, sensor_data: List[Dict]) -> str:
        """Enqueue batch ML prediction task"""
        pass
    
    def get_task_status(self, task_id: str) -> Dict:
        """Check task status and retrieve result"""
        pass
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel pending or running task"""
        pass

@celery_app.task
def process_food_image(image_path: str, user_id: str) -> Dict:
    """Celery task for food image processing"""
    pass

@celery_app.task
def batch_predict_risk(sensor_readings: List[Dict]) -> List[Dict]:
    """Celery task for batch risk prediction"""
    pass
```

**Responsibilities**:
- Manage Celery worker pool
- Queue long-running vision and ML tasks
- Provide task status tracking
- Handle task retries and error recovery
- Support priority-based task scheduling

### Component 4: Optimized ML Pipeline

**Purpose**: Optimize ML model inference with quantization, batching, and caching

**Interface**:
```python
from typing import List, Tuple
import numpy as np

class OptimizedMLPipeline:
    def predict_risk_batch(self, features: np.ndarray) -> Tuple[List[str], List[float]]:
        """Batch predict risk levels with confidence scores"""
        pass
    
    def detect_anomalies_batch(self, features: np.ndarray) -> List[bool]:
        """Batch detect anomalies in sensor data"""
        pass
    
    def forecast_conditions(self, historical_data: np.ndarray, horizon: int) -> np.ndarray:
        """Forecast future environmental conditions"""
        pass
    
    def quantize_model(self, model_path: str, quantization_type: str) -> None:
        """Apply quantization to reduce model size"""
        pass
    
    def warm_up_models(self) -> None:
        """Pre-load all models into memory"""
        pass

class ModelOptimizationConfig:
    use_onnx_runtime: bool  # Convert to ONNX for faster inference
    quantization_bits: int  # 8 for int8, 16 for fp16
    batch_size: int  # Optimal batch size for inference
    enable_gpu: bool  # Use GPU acceleration if available
    cache_predictions: bool  # Cache recent predictions
```

**Responsibilities**:
- Load and manage optimized ML models
- Implement batch inference for efficiency
- Apply model quantization (int8/fp16)
- Convert models to ONNX format
- Cache frequent predictions

### Component 5: Database Service

**Purpose**: Migrate from SQLite to PostgreSQL with connection pooling and query optimization

**Interface**:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

class DatabaseService:
    async def store_sensor_data_batch(self, readings: List[Dict]) -> None:
        """Bulk insert sensor readings"""
        pass
    
    async def get_recent_sensor_data(self, limit: int, offset: int) -> List[Dict]:
        """Retrieve recent sensor data with pagination"""
        pass
    
    async def store_food_analysis(self, analysis: Dict) -> int:
        """Store food analysis result"""
        pass
    
    async def get_analysis_by_image_hash(self, image_hash: str) -> Optional[Dict]:
        """Retrieve cached analysis by image hash"""
        pass
    
    async def create_indexes(self) -> None:
        """Create database indexes for query optimization"""
        pass

class DatabaseConfig:
    connection_pool_size: int  # 20 connections
    max_overflow: int  # 10 additional connections
    pool_timeout: int  # 30 seconds
    enable_query_logging: bool
    use_prepared_statements: bool
```

**Responsibilities**:
- Manage PostgreSQL connection pool
- Implement async database operations
- Optimize queries with proper indexing
- Support bulk insert operations
- Handle database migrations

## Data Models

### Model 1: VisionAnalysisResult

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class VisionAnalysisResult(BaseModel):
    food_item: str = Field(..., description="Detected food item name")
    ingredients: List[str] = Field(..., description="List of detected ingredients")
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    detected_allergens: List[str] = Field(default_factory=list)
    risk_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH|CRITICAL)$")
    processing_time_ms: float
    model_version: str
    image_hash: str = Field(..., description="Perceptual hash for deduplication")
    embeddings: Optional[List[float]] = Field(None, description="Image embeddings")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

**Validation Rules**:
- confidence_score must be between 0.0 and 1.0
- risk_level must be one of: LOW, MEDIUM, HIGH, CRITICAL
- ingredients list must not be empty
- image_hash must be unique for deduplication

### Model 2: OptimizedSensorReading

```python
class OptimizedSensorReading(BaseModel):
    temperature: float = Field(..., ge=-50.0, le=100.0)
    humidity: float = Field(..., ge=0.0, le=100.0)
    dust: float = Field(..., ge=0.0, le=1000.0)
    timestamp: datetime
    device_id: str
    batch_id: Optional[str] = None  # For batch processing
    
class SensorBatchRequest(BaseModel):
    readings: List[OptimizedSensorReading] = Field(..., max_items=100)
    priority: int = Field(default=1, ge=1, le=5)
    
class SensorBatchResponse(BaseModel):
    predictions: List[Dict]
    processing_time_ms: float
    batch_size: int
    cache_hits: int
```

**Validation Rules**:
- Temperature range: -50°C to 100°C
- Humidity range: 0% to 100%
- Dust range: 0 to 1000 µg/m³
- Batch size limited to 100 readings per request
- Priority level: 1 (lowest) to 5 (highest)

### Model 3: CacheEntry

```python
class CacheEntry(BaseModel):
    key: str
    value: Any
    ttl_seconds: int
    created_at: datetime
    hit_count: int = 0
    last_accessed: datetime
    
class CacheMetrics(BaseModel):
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    avg_response_time_ms: float
    memory_usage_mb: float
```

**Validation Rules**:
- TTL must be positive integer
- hit_rate calculated as hits / (hits + misses)
- Memory usage tracked for cache eviction policies

## Algorithmic Pseudocode

### Main Processing Algorithm

```pascal
ALGORITHM processOptimizedFoodAnalysis(imageData)
INPUT: imageData of type ImageUpload
OUTPUT: result of type VisionAnalysisResult

BEGIN
  ASSERT imageData.size <= MAX_IMAGE_SIZE
  ASSERT imageData.format IN SUPPORTED_FORMATS
  
  // Step 1: Generate perceptual hash for deduplication
  imageHash ← computePerceptualHash(imageData)
  
  // Step 2: Check cache for existing analysis
  cachedResult ← cache.get(imageHash)
  IF cachedResult IS NOT NULL THEN
    cachedResult.hit_count ← cachedResult.hit_count + 1
    RETURN cachedResult
  END IF
  
  // Step 3: Load optimized vision model
  model ← loadVisionModel(MODEL_CONFIG)
  ASSERT model.isLoaded() = true
  
  // Step 4: Generate image embeddings
  embeddings ← model.generateEmbeddings(imageData)
  
  // Step 5: Check similarity with known foods
  similarFood ← findSimilarFood(embeddings, SIMILARITY_THRESHOLD)
  IF similarFood IS NOT NULL AND similarFood.confidence > 0.9 THEN
    result ← createResultFromCache(similarFood)
    RETURN result
  END IF
  
  // Step 6: Perform vision analysis
  startTime ← getCurrentTime()
  analysis ← model.analyzeFood(imageData)
  processingTime ← getCurrentTime() - startTime
  
  // Step 7: Match allergens
  allergens ← matchAllergens(analysis.ingredients)
  riskLevel ← evaluateRisk(allergens)
  
  // Step 8: Create result object
  result ← VisionAnalysisResult(
    food_item: analysis.food_item,
    ingredients: analysis.ingredients,
    confidence_score: analysis.confidence,
    detected_allergens: allergens,
    risk_level: riskLevel,
    processing_time_ms: processingTime,
    model_version: MODEL_VERSION,
    image_hash: imageHash,
    embeddings: embeddings
  )
  
  // Step 9: Store in cache and database
  cache.set(imageHash, result, CACHE_TTL)
  database.storeAnalysis(result)
  
  ASSERT result.confidence_score >= 0.0 AND result.confidence_score <= 1.0
  ASSERT result.risk_level IN ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
  
  RETURN result
END
```

**Preconditions**:
- imageData is valid and within size limits
- Vision model is loaded and ready
- Cache and database connections are active
- Allergen database is accessible

**Postconditions**:
- Result contains valid food analysis
- Result is cached for future requests
- Analysis is persisted to database
- Processing time is recorded for metrics

**Loop Invariants**: N/A (no loops in main algorithm)

### Batch Inference Algorithm

```pascal
ALGORITHM batchPredictRisk(sensorReadings)
INPUT: sensorReadings of type List<SensorReading>
OUTPUT: predictions of type List<RiskPrediction>

BEGIN
  ASSERT sensorReadings.length > 0
  ASSERT sensorReadings.length <= MAX_BATCH_SIZE
  
  predictions ← empty list
  cacheHits ← 0
  
  // Step 1: Separate cached and uncached readings
  uncachedReadings ← empty list
  
  FOR each reading IN sensorReadings DO
    ASSERT isValidReading(reading) = true
    
    cacheKey ← generateCacheKey(reading)
    cachedPrediction ← cache.get(cacheKey)
    
    IF cachedPrediction IS NOT NULL THEN
      predictions.add(cachedPrediction)
      cacheHits ← cacheHits + 1
    ELSE
      uncachedReadings.add(reading)
    END IF
  END FOR
  
  // Step 2: Batch predict uncached readings
  IF uncachedReadings.length > 0 THEN
    features ← extractFeatures(uncachedReadings)
    ASSERT features.shape[0] = uncachedReadings.length
    
    // Load optimized model
    model ← loadOptimizedModel(RISK_MODEL_PATH)
    
    // Batch inference
    batchPredictions ← model.predictBatch(features)
    
    // Step 3: Store predictions in cache
    FOR i FROM 0 TO uncachedReadings.length - 1 DO
      prediction ← batchPredictions[i]
      cacheKey ← generateCacheKey(uncachedReadings[i])
      cache.set(cacheKey, prediction, PREDICTION_CACHE_TTL)
      predictions.add(prediction)
    END FOR
  END IF
  
  ASSERT predictions.length = sensorReadings.length
  
  RETURN predictions
END
```

**Preconditions**:
- sensorReadings is non-empty list
- Batch size does not exceed MAX_BATCH_SIZE
- All readings have valid sensor values
- ML model is loaded and ready

**Postconditions**:
- Returns prediction for each input reading
- Predictions are cached for future requests
- Cache hit rate is tracked
- All predictions have valid risk levels

**Loop Invariants**:
- All processed readings have corresponding predictions
- Cache hit count accurately reflects cached predictions
- Uncached readings list contains only readings not in cache

### Model Optimization Algorithm

```pascal
ALGORITHM optimizeMLModel(modelPath, optimizationConfig)
INPUT: modelPath of type String, optimizationConfig of type OptimizationConfig
OUTPUT: optimizedModel of type Model

BEGIN
  ASSERT fileExists(modelPath) = true
  ASSERT optimizationConfig.isValid() = true
  
  // Step 1: Load original model
  originalModel ← loadModel(modelPath)
  modelSize ← getModelSize(originalModel)
  
  // Step 2: Convert to ONNX if enabled
  IF optimizationConfig.use_onnx_runtime = true THEN
    onnxModel ← convertToONNX(originalModel)
    originalModel ← onnxModel
  END IF
  
  // Step 3: Apply quantization
  IF optimizationConfig.quantization_bits < 32 THEN
    quantizedModel ← quantizeModel(
      originalModel,
      optimizationConfig.quantization_bits
    )
    originalModel ← quantizedModel
  END IF
  
  // Step 4: Optimize for target device
  IF optimizationConfig.enable_gpu = true THEN
    optimizedModel ← moveToGPU(originalModel)
  ELSE
    optimizedModel ← optimizeForCPU(originalModel)
  END IF
  
  // Step 5: Validate optimization
  testData ← generateTestData()
  originalPredictions ← originalModel.predict(testData)
  optimizedPredictions ← optimizedModel.predict(testData)
  
  accuracy ← compareAccuracy(originalPredictions, optimizedPredictions)
  ASSERT accuracy >= MIN_ACCURACY_THRESHOLD
  
  optimizedSize ← getModelSize(optimizedModel)
  compressionRatio ← modelSize / optimizedSize
  
  RETURN optimizedModel
END
```

**Preconditions**:
- Model file exists at specified path
- Optimization configuration is valid
- Test data is available for validation
- Target device (CPU/GPU) is available

**Postconditions**:
- Optimized model maintains accuracy above threshold
- Model size is reduced through quantization
- Model is ready for inference on target device
- Compression ratio is calculated and logged

**Loop Invariants**: N/A (no loops in main algorithm)

## Key Functions with Formal Specifications

### Function 1: computePerceptualHash()

```python
def computePerceptualHash(image: Image) -> str:
    """Generate perceptual hash for image deduplication"""
    pass
```

**Preconditions:**
- image is valid PIL Image object
- image is not corrupted
- image has at least 8x8 pixels

**Postconditions:**
- Returns 64-character hexadecimal string
- Identical images produce identical hashes
- Similar images produce similar hashes (Hamming distance < 10)
- Hash is deterministic for same input

**Loop Invariants:** N/A

### Function 2: loadOptimizedModel()

```python
def loadOptimizedModel(model_path: str, config: ModelConfig) -> Model:
    """Load and optimize ML model for inference"""
    pass
```

**Preconditions:**
- model_path points to valid model file
- config contains valid optimization parameters
- Sufficient memory available for model loading
- Target device (CPU/GPU) is available

**Postconditions:**
- Returns loaded model ready for inference
- Model is quantized according to config
- Model is moved to target device
- Model passes validation checks

**Loop Invariants:** N/A

### Function 3: batchInference()

```python
def batchInference(model: Model, features: np.ndarray, batch_size: int) -> np.ndarray:
    """Perform batch inference with optimal batch size"""
    pass
```

**Preconditions:**
- model is loaded and ready
- features is 2D numpy array with shape (n_samples, n_features)
- batch_size is positive integer
- n_samples > 0

**Postconditions:**
- Returns predictions array with shape (n_samples,)
- All samples are processed exactly once
- Predictions maintain order of input features
- No data loss during batching

**Loop Invariants:**
- All processed batches have predictions stored
- Remaining samples count decreases by batch_size each iteration
- Total predictions count equals processed samples count

### Function 4: cacheWithTTL()

```python
def cacheWithTTL(key: str, value: Any, ttl: timedelta) -> bool:
    """Store value in cache with time-to-live"""
    pass
```

**Preconditions:**
- key is non-empty string
- value is serializable
- ttl is positive timedelta
- Cache connection is active

**Postconditions:**
- Value is stored in cache with specified TTL
- Returns true if storage successful
- Cache entry expires after TTL
- Subsequent get(key) returns value until expiration

**Loop Invariants:** N/A

## Example Usage

```python
# Example 1: Optimized food image analysis
from vision_service import VisionModelService
from cache_service import CacheService

vision_service = VisionModelService(
    model_name="Salesforce/blip2-opt-2.7b",
    device="cuda",
    quantization="int8"
)
cache_service = CacheService(redis_url="redis://localhost:6379")

# Analyze food image with caching
image = Image.open("food.jpg")
result = vision_service.analyze_food_image(image, use_cache=True)

print(f"Food: {result.food_item}")
print(f"Ingredients: {result.ingredients}")
print(f"Risk Level: {result.risk_level}")
print(f"Processing Time: {result.processing_time_ms}ms")

# Example 2: Batch sensor prediction
from ml_pipeline import OptimizedMLPipeline

ml_pipeline = OptimizedMLPipeline(
    use_onnx_runtime=True,
    quantization_bits=8,
    batch_size=32
)

sensor_readings = [
    {"temperature": 25.5, "humidity": 60.0, "dust": 35.0},
    {"temperature": 26.0, "humidity": 62.0, "dust": 40.0},
    # ... more readings
]

features = np.array([[r["temperature"], r["humidity"], r["dust"]] 
                     for r in sensor_readings])
risk_levels, confidences = ml_pipeline.predict_risk_batch(features)

for i, (risk, conf) in enumerate(zip(risk_levels, confidences)):
    print(f"Reading {i}: Risk={risk}, Confidence={conf:.2f}")

# Example 3: Async task processing
from task_queue import TaskQueue

task_queue = TaskQueue(broker_url="redis://localhost:6379")

# Enqueue vision analysis task
task_id = task_queue.enqueue_vision_analysis(
    image_path="uploads/food.jpg",
    user_id="user123"
)

# Check task status
status = task_queue.get_task_status(task_id)
print(f"Task Status: {status['state']}")

if status['state'] == 'SUCCESS':
    result = status['result']
    print(f"Analysis Complete: {result}")

# Example 4: Database batch operations
from database_service import DatabaseService

db_service = DatabaseService(
    connection_string="postgresql://user:pass@localhost/avaris"
)

# Bulk insert sensor readings
await db_service.store_sensor_data_batch(sensor_readings)

# Query with pagination
recent_data = await db_service.get_recent_sensor_data(limit=100, offset=0)
```

## Correctness Properties

### Property 1: Cache Consistency
```python
# For any image hash, cached result must match fresh computation
∀ image_hash, image_data:
    cached_result = cache.get(image_hash)
    fresh_result = vision_model.analyze(image_data)
    ⟹ (cached_result is None) ∨ (cached_result.food_item == fresh_result.food_item)
```

### Property 2: Batch Processing Completeness
```python
# All input readings must have corresponding predictions
∀ sensor_batch:
    predictions = batch_predict_risk(sensor_batch)
    ⟹ len(predictions) == len(sensor_batch)
    ∧ ∀i ∈ [0, len(sensor_batch)): predictions[i].reading_id == sensor_batch[i].id
```

### Property 3: Model Optimization Accuracy
```python
# Optimized model must maintain accuracy within threshold
∀ model, test_data:
    original_accuracy = evaluate(model, test_data)
    optimized_model = optimize(model, config)
    optimized_accuracy = evaluate(optimized_model, test_data)
    ⟹ optimized_accuracy >= original_accuracy - ACCURACY_TOLERANCE
```

### Property 4: Cache TTL Enforcement
```python
# Cached entries must expire after TTL
∀ key, value, ttl:
    cache.set(key, value, ttl)
    ⟹ (time_elapsed < ttl ⟹ cache.get(key) == value)
    ∧ (time_elapsed >= ttl ⟹ cache.get(key) is None)
```

### Property 5: Perceptual Hash Similarity
```python
# Similar images must produce similar hashes
∀ image1, image2:
    similarity(image1, image2) > SIMILARITY_THRESHOLD
    ⟹ hamming_distance(hash(image1), hash(image2)) < MAX_HAMMING_DISTANCE
```

## Error Handling

### Error Scenario 1: Vision Model Loading Failure

**Condition**: Model file is corrupted or incompatible with current runtime
**Response**: 
- Log error with model path and exception details
- Fall back to alternative model (CLIP if BLIP-2 fails)
- Return error response with 503 status code
**Recovery**: 
- Retry with exponential backoff (3 attempts)
- Download fresh model weights if corruption detected
- Alert monitoring system for manual intervention

### Error Scenario 2: Cache Connection Loss

**Condition**: Redis server is unreachable or connection times out
**Response**:
- Log warning about cache unavailability
- Continue processing without cache (degraded mode)
- Return results with cache_hit=false flag
**Recovery**:
- Implement circuit breaker pattern (open after 5 failures)
- Retry connection every 30 seconds
- Resume caching when connection restored

### Error Scenario 3: Database Connection Pool Exhaustion

**Condition**: All database connections in pool are in use
**Response**:
- Queue request with timeout (30 seconds)
- Return 429 Too Many Requests if timeout exceeded
- Log pool exhaustion event for capacity planning
**Recovery**:
- Increase pool size dynamically if sustained high load
- Implement connection leak detection
- Force close idle connections after timeout

### Error Scenario 4: Batch Processing Partial Failure

**Condition**: Some items in batch fail processing while others succeed
**Response**:
- Process successful items and store results
- Collect failed items with error details
- Return partial success response with error list
**Recovery**:
- Retry failed items individually (not in batch)
- Mark permanently failed items for manual review
- Update batch processing metrics

### Error Scenario 5: Model Quantization Accuracy Drop

**Condition**: Quantized model accuracy falls below threshold
**Response**:
- Reject quantized model and keep original
- Log quantization failure with accuracy metrics
- Alert ML team for model retraining
**Recovery**:
- Try alternative quantization method (int8 → fp16)
- Adjust quantization parameters
- Fall back to full precision model if necessary

## Testing Strategy

### Unit Testing Approach

Test individual components in isolation with mocked dependencies:

- Vision Model Service: Test with sample images, verify output format, check error handling
- Cache Service: Test TTL enforcement, key generation, invalidation patterns
- ML Pipeline: Test batch processing, model loading, quantization accuracy
- Database Service: Test CRUD operations, connection pooling, query optimization

Coverage goals: 85% line coverage, 90% branch coverage for critical paths

Key test cases:
- Valid input processing with expected outputs
- Invalid input handling (malformed data, out-of-range values)
- Edge cases (empty batches, maximum batch size, cache misses)
- Error scenarios (connection failures, model loading errors)

### Property-Based Testing Approach

Use property-based testing to verify system invariants across random inputs:

**Property Test Library**: Hypothesis (Python)

**Test Properties**:
1. Cache consistency: Cached results match fresh computations
2. Batch completeness: Output size equals input size for all batches
3. Hash determinism: Same image always produces same hash
4. Model accuracy: Optimized model maintains accuracy threshold
5. TTL enforcement: Cache entries expire correctly

**Test Strategy**:
- Generate random sensor readings within valid ranges
- Generate random images with varying properties
- Test with random batch sizes (1 to MAX_BATCH_SIZE)
- Verify invariants hold across all generated inputs

### Integration Testing Approach

Test component interactions and end-to-end workflows:

- API → Cache → Database flow
- API → Task Queue → Worker → Model flow
- Vision analysis with real images
- Batch prediction with real sensor data
- Cache invalidation and refresh scenarios

Test environments:
- Local: Docker Compose with all services
- Staging: Kubernetes cluster with production-like config
- Load testing: Simulate 1000 concurrent requests

Performance benchmarks:
- Food image analysis: < 500ms (with cache), < 2s (without cache)
- Sensor prediction: < 50ms (batch of 10)
- Cache hit rate: > 70% for repeated requests
- Database query time: < 100ms for recent data queries

## Performance Considerations

### Target Performance Metrics

- Food image analysis latency: 
  - Cache hit: < 50ms
  - Cache miss: < 2s (down from 5-10s with Gemini API)
- Sensor prediction latency:
  - Single prediction: < 20ms
  - Batch of 10: < 50ms (5ms per sample)
- API response time (p95): < 200ms
- Cache hit rate: > 70%
- Database query time (p95): < 100ms
- System throughput: 100 requests/second

### Optimization Strategies

1. Model Optimization:
   - Use BLIP-2 2.7B model (smaller than Gemini, faster inference)
   - Apply int8 quantization (4x memory reduction, 2-3x speedup)
   - Convert to ONNX Runtime (20-30% inference speedup)
   - Batch processing for sensor predictions (10x throughput improvement)

2. Caching Strategy:
   - Redis for in-memory caching (sub-millisecond access)
   - Perceptual hashing for image deduplication (70% cache hit rate expected)
   - Multi-level cache: L1 (in-process), L2 (Redis)
   - Cache warming on startup for frequent queries

3. Database Optimization:
   - PostgreSQL with connection pooling (20 connections)
   - Indexes on timestamp, image_hash, device_id columns
   - Bulk insert for sensor data (100x faster than individual inserts)
   - Async queries with SQLAlchemy async engine

4. Async Processing:
   - Celery task queue for long-running operations
   - WebSocket notifications for async results
   - Priority queues for critical tasks
   - Worker auto-scaling based on queue depth

5. Resource Management:
   - Model pre-loading on worker startup (eliminate cold start)
   - GPU memory management for vision model
   - Connection pool tuning for database
   - Rate limiting to prevent resource exhaustion

## Security Considerations

### Authentication & Authorization

- API key authentication for external requests
- JWT tokens for user sessions
- Role-based access control (RBAC) for admin endpoints
- Rate limiting per API key (100 requests/minute)

### Data Protection

- Image data encrypted at rest (AES-256)
- Database connections use TLS
- Redis connections use TLS and authentication
- Sensitive data (allergen profiles) encrypted in database

### Input Validation

- Image size limits (max 10MB)
- File type validation (JPEG, PNG only)
- Sensor value range validation
- SQL injection prevention (parameterized queries)
- XSS prevention in API responses

### Model Security

- Model files integrity verification (checksums)
- Sandboxed model execution environment
- Resource limits for model inference (timeout, memory)
- Model versioning and rollback capability

### Monitoring & Auditing

- Log all API requests with timestamps
- Track failed authentication attempts
- Monitor for unusual patterns (DDoS, data exfiltration)
- Audit trail for sensitive operations

## Dependencies

### Core Dependencies

- FastAPI 0.104+ (async web framework)
- PostgreSQL 15+ (database)
- Redis 7+ (caching and task queue)
- Celery 5+ (distributed task queue)

### ML/AI Dependencies

- PyTorch 2.0+ (deep learning framework)
- Transformers 4.35+ (Hugging Face models)
- ONNX Runtime 1.16+ (optimized inference)
- Pillow 10+ (image processing)
- scikit-learn 1.3+ (traditional ML models)

### Vision Model Options

Option 1: BLIP-2 (Salesforce/blip2-opt-2.7b)
- Pros: Excellent food recognition, detailed descriptions, 2.7B parameters
- Cons: Requires 6GB GPU memory, slower than CLIP
- Use case: High accuracy food analysis

Option 2: CLIP (openai/clip-vit-large-patch14)
- Pros: Fast inference, good zero-shot classification, 428M parameters
- Cons: Less detailed descriptions than BLIP-2
- Use case: Real-time ingredient detection with embeddings

Recommendation: Start with BLIP-2 for accuracy, fall back to CLIP for speed

### Infrastructure Dependencies

- Docker 24+ (containerization)
- Kubernetes 1.28+ (orchestration, optional)
- Nginx (reverse proxy and load balancing)
- Prometheus + Grafana (monitoring)

### Development Dependencies

- pytest 7+ (testing framework)
- hypothesis 6+ (property-based testing)
- black (code formatting)
- mypy (type checking)
- locust (load testing)
