"""
Text Analysis Module using Gemini AI
Handles all text-based analysis, explanations, and reasoning
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GeminiTextAnalyzer:
    """Gemini AI for text analysis and explanations"""
    
    def __init__(self):
        self.model = None
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure Gemini API"""
        # Try hardcoded key first (for development)
        hardcoded_key = ""
        
        api_key = None
        if hardcoded_key and hardcoded_key not in ["", "YOUR_API_KEY_HERE"]:
            api_key = hardcoded_key
            logger.info("Using hardcoded Gemini API key")
        else:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key and api_key != "YOUR_API_KEY_HERE":
                logger.info("Using Gemini API key from environment")
        
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("Gemini text analyzer configured successfully")
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")
                self.model = None
        else:
            logger.warning("Gemini API key not found")
            self.model = None
    
    def generate_text(self, prompt: str) -> str:
        """
        Generate text response using Gemini
        
        Args:
            prompt (str): The prompt for text generation
            
        Returns:
            str: Generated text response
        """
        if not self.model:
            logger.warning("Gemini not configured, returning fallback response")
            return "AI analysis unavailable. Please configure Gemini API key."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return f"Error generating AI response: {str(e)}"
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.model is not None

# Global text analyzer instance
_text_analyzer = None

def get_text_analyzer() -> GeminiTextAnalyzer:
    """Get the global text analyzer instance"""
    global _text_analyzer
    if _text_analyzer is None:
        _text_analyzer = GeminiTextAnalyzer()
    return _text_analyzer

def generate_ai_text(prompt: str) -> str:
    """
    Convenience function to generate AI text
    
    Args:
        prompt (str): The prompt for text generation
        
    Returns:
        str: Generated text response
    """
    analyzer = get_text_analyzer()
    return analyzer.generate_text(prompt)