# Frontend Integration Guide

## API Response Format

The `/api/upload-food-image` endpoint returns:

```json
{
  "food_item": "Fried Chicken Burger",
  "ingredients": ["burger bun", "fried chicken", "processed cheese slice", "milk", "breadcrumbs", "wheat flour"],
  "detected_allergens": ["dairy", "gluten"],
  "risk_level": "HIGH",
  "confidence": 0.95,
  "ai_explanation": "**AVARIS Food Safety Alert: Fried Chicken Burger**\n\n**Detected Allergens:** Dairy, Gluten\n**Risk Level:** HIGH\n\n**Why it's a risk:**\nThis Fried Chicken Burger poses a **HIGH risk** for individuals with dairy and gluten allergies...",
  "image_url": "/uploads/food_images/food_20260313_120000.jpg"
}
```

## Important: Markdown Formatting

The `ai_explanation` field contains **markdown-formatted text** with:
- `**bold text**` for emphasis
- `*italic text*` for emphasis
- Bullet points with `*` or `-`
- Line breaks with `\n`

### ❌ Wrong: Display as Plain Text
```jsx
<p>{response.ai_explanation}</p>
```
This will show: `**AVARIS Food Safety Alert**` (with asterisks)

### ✅ Correct: Render Markdown as HTML

You need to convert markdown to HTML before displaying.

## React/Next.js Implementation

### Option 1: Using `react-markdown` (Recommended)

Install the package:
```bash
npm install react-markdown
```

Use in your component:
```jsx
import ReactMarkdown from 'react-markdown';

function FoodAnalysisResult({ analysis }) {
  return (
    <div className="analysis-result">
      <h2>{analysis.food_item}</h2>
      
      <div className="allergens">
        <strong>Detected Allergens:</strong>
        {analysis.detected_allergens.map(allergen => (
          <span key={allergen} className="allergen-badge">
            {allergen}
          </span>
        ))}
      </div>
      
      <div className={`risk-level risk-${analysis.risk_level.toLowerCase()}`}>
        Risk Level: {analysis.risk_level}
      </div>
      
      {/* Render markdown explanation as HTML */}
      <div className="ai-explanation">
        <ReactMarkdown>{analysis.ai_explanation}</ReactMarkdown>
      </div>
    </div>
  );
}
```

### Option 2: Using `marked` Library

Install the package:
```bash
npm install marked
```

Use in your component:
```jsx
import { marked } from 'marked';

function FoodAnalysisResult({ analysis }) {
  // Convert markdown to HTML
  const explanationHtml = marked(analysis.ai_explanation);
  
  return (
    <div className="analysis-result">
      <h2>{analysis.food_item}</h2>
      
      {/* Render HTML */}
      <div 
        className="ai-explanation"
        dangerouslySetInnerHTML={{ __html: explanationHtml }}
      />
    </div>
  );
}
```

### Option 3: Simple Regex Replacement (Basic)

If you don't want to add dependencies:

```jsx
function FoodAnalysisResult({ analysis }) {
  // Simple markdown to HTML conversion
  const formatMarkdown = (text) => {
    return text
      // Bold: **text** -> <strong>text</strong>
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      // Italic: *text* -> <em>text</em>
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Line breaks: \n -> <br>
      .replace(/\n/g, '<br>')
      // Bullet points: * item -> <li>item</li>
      .replace(/^\* (.+)$/gm, '<li>$1</li>')
      // Wrap lists
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
  };
  
  const explanationHtml = formatMarkdown(analysis.ai_explanation);
  
  return (
    <div className="analysis-result">
      <div 
        className="ai-explanation"
        dangerouslySetInnerHTML={{ __html: explanationHtml }}
      />
    </div>
  );
}
```

## Vanilla JavaScript Implementation

```javascript
// Fetch and display food analysis
async function uploadFoodImage(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch('/api/upload-food-image', {
    method: 'POST',
    body: formData
  });
  
  const analysis = await response.json();
  
  // Convert markdown to HTML
  const explanationHtml = convertMarkdownToHtml(analysis.ai_explanation);
  
  // Display in DOM
  document.getElementById('food-item').textContent = analysis.food_item;
  document.getElementById('risk-level').textContent = analysis.risk_level;
  document.getElementById('ai-explanation').innerHTML = explanationHtml;
}

// Simple markdown to HTML converter
function convertMarkdownToHtml(markdown) {
  return markdown
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
    .replace(/^\* (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
}
```

## Vue.js Implementation

```vue
<template>
  <div class="analysis-result">
    <h2>{{ analysis.food_item }}</h2>
    
    <div class="risk-level" :class="`risk-${analysis.risk_level.toLowerCase()}`">
      Risk Level: {{ analysis.risk_level }}
    </div>
    
    <!-- Render markdown as HTML -->
    <div class="ai-explanation" v-html="formattedExplanation"></div>
  </div>
</template>

<script>
import { marked } from 'marked';

export default {
  props: ['analysis'],
  computed: {
    formattedExplanation() {
      return marked(this.analysis.ai_explanation);
    }
  }
}
</script>
```

## Styling Recommendations

Add CSS to style the rendered markdown:

```css
.ai-explanation {
  font-size: 16px;
  line-height: 1.6;
  color: #333;
}

.ai-explanation strong {
  font-weight: 700;
  color: #d32f2f; /* Red for emphasis */
}

.ai-explanation ul {
  margin: 10px 0;
  padding-left: 20px;
}

.ai-explanation li {
  margin: 5px 0;
}

.risk-high {
  background-color: #ffebee;
  color: #c62828;
  padding: 10px;
  border-left: 4px solid #c62828;
}

.risk-medium {
  background-color: #fff3e0;
  color: #ef6c00;
  padding: 10px;
  border-left: 4px solid #ef6c00;
}

.risk-low {
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 10px;
  border-left: 4px solid #2e7d32;
}
```

## Example: Complete React Component

```jsx
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './FoodAnalysis.css';

function FoodAnalysisUpload() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', file);

    try {
      const response = await fetch('http://localhost:8000/api/upload-food-image', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="food-analysis-container">
      <h1>AVARIS Food Allergen Detector</h1>
      
      <input 
        type="file" 
        accept="image/*" 
        onChange={handleImageUpload}
        disabled={loading}
      />

      {loading && <div className="loading">Analyzing image...</div>}
      {error && <div className="error">{error}</div>}

      {analysis && (
        <div className="analysis-result">
          <img 
            src={`http://localhost:8000${analysis.image_url}`} 
            alt={analysis.food_item}
            className="food-image"
          />
          
          <h2>{analysis.food_item}</h2>
          
          <div className="confidence">
            Confidence: {(analysis.confidence * 100).toFixed(1)}%
          </div>

          <div className="ingredients">
            <h3>Ingredients:</h3>
            <ul>
              {analysis.ingredients.map((ingredient, index) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>
          </div>

          <div className="allergens">
            <h3>Detected Allergens:</h3>
            {analysis.detected_allergens.length > 0 ? (
              <div className="allergen-badges">
                {analysis.detected_allergens.map((allergen, index) => (
                  <span key={index} className="allergen-badge">
                    {allergen}
                  </span>
                ))}
              </div>
            ) : (
              <p>No allergens detected</p>
            )}
          </div>

          <div className={`risk-level risk-${analysis.risk_level.toLowerCase()}`}>
            <strong>Risk Level:</strong> {analysis.risk_level}
          </div>

          {/* Render markdown explanation as HTML */}
          <div className="ai-explanation">
            <ReactMarkdown>{analysis.ai_explanation}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default FoodAnalysisUpload;
```

## Security Note

When using `dangerouslySetInnerHTML` or rendering HTML from API responses:
- The backend (AVARIS) generates the markdown, so it's trusted
- However, always sanitize if you allow user-generated content
- Use libraries like `DOMPurify` for additional security:

```bash
npm install dompurify
```

```jsx
import DOMPurify from 'dompurify';
import { marked } from 'marked';

const explanationHtml = DOMPurify.sanitize(marked(analysis.ai_explanation));
```

## Summary

1. **Backend (AVARIS)**: Returns markdown-formatted text in `ai_explanation`
2. **Frontend**: Must convert markdown to HTML before displaying
3. **Recommended**: Use `react-markdown` or `marked` library
4. **Alternative**: Simple regex replacement for basic formatting
5. **Styling**: Add CSS to make the explanation visually appealing

This ensures that bold text (`**text**`) displays as **text** instead of `**text**` in the frontend!