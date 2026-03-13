# Gemini API Setup Guide

## Overview
AVARIS uses Google's Gemini AI for intelligent analysis of environmental conditions and food allergen detection. To use these features, you need to configure your Gemini API key.

## Getting Your Gemini API Key

1. **Visit Google AI Studio**
   - Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account

2. **Create API Key**
   - Click "Create API Key"
   - Choose "Create API key in new project" or select an existing project
   - Copy the generated API key (starts with `AIzaSy...`)

3. **Configure AVARIS**
   - Open the `.env` file in the `avaris` directory
   - Find the line: `GEMINI_API_KEY=""`
   - Paste your API key between the quotes:
     ```
     GEMINI_API_KEY="AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
     ```
   - Save the file

## Features Enabled by Gemini API

### 🧠 Environment Analysis
- Intelligent analysis of temperature, humidity, and dust levels
- Risk assessment and recommendations
- Contextual explanations for environmental conditions

### 🥗 Food Allergen Detection
- Visual analysis of food images
- Ingredient identification
- Allergen detection and risk assessment
- Safety recommendations

## Security Notes

- **Keep your API key secure**: Never commit the `.env` file with your actual API key to version control
- **Environment variables**: The API key is loaded from environment variables for security
- **Local storage**: Your API key is only stored locally in the `.env` file

## Troubleshooting

### API Key Not Working
- Verify the key is correctly pasted in `.env`
- Ensure there are no extra spaces or characters
- Check that the Gemini API is enabled in your Google Cloud project

### Features Not Available
If Gemini features are not working:
1. Check the backend logs for API key errors
2. Verify your API key has sufficient quota
3. Ensure internet connectivity for API calls

### Fallback Behavior
When Gemini API is not configured:
- Environment analysis will show "AI analysis unavailable"
- Food analysis will use basic pattern matching
- Core monitoring features continue to work normally

## Cost Information

- Gemini API has a generous free tier
- Check current pricing at [https://ai.google.dev/pricing](https://ai.google.dev/pricing)
- AVARIS only makes API calls when:
  - User clicks "Analyze Environment" button
  - User analyzes food images
  - No continuous/background API usage

## Example Configuration

Your `.env` file should look like this:
```bash
# AI API Keys
# Get your Gemini API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY="AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Other configuration...
MISTRAL_MODEL_PATH="./models/mistral_4b"
ESP32_IP="YOUR_ESP32_IP"
# ... rest of configuration
```

## Testing Your Setup

After configuring your API key:
1. Restart the AVARIS backend server
2. Check the logs for "Gemini configured successfully" messages
3. Test the Environment Analysis panel
4. Try uploading a food image for analysis

If you see success messages in the logs, your Gemini API is properly configured!