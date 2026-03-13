"""
Text Analysis Module using Gemini AI
Handles all text-based analysis, explanations, and reasoning
"""

# Python 3.13 compatibility fix for cgi module
import sys
if sys.version_info >= (3, 13):
    try:
        import cgi
    except ImportError:
        # Create a minimal cgi module stub for Python 3.13 compatibility
        import types
        import html
        
        cgi = types.ModuleType('cgi')
        # Provide the most commonly used cgi functions
        cgi.escape = html.escape  # html.escape is the modern replacement
        cgi.parse_qs = lambda qs, keep_blank_values=False, strict_parsing=False: {}
        cgi.parse_qsl = lambda qs, keep_blank_values=False, strict_parsing=False: []
        
        # Add to sys.modules so other imports can find it
        sys.modules['cgi'] = cgi

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
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key or api_key.strip() == "":
            logger.warning("GEMINI_API_KEY not found in environment variables")
            self.model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Gemini text analyzer configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure Gemini: {e}")
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
            return "AI analysis unavailable. Please configure your GEMINI_API_KEY in the .env file. See GEMINI_API_SETUP.md for instructions."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating text with Gemini: {e}")
            return f"Error generating AI response: {str(e)}. Please check your GEMINI_API_KEY configuration."
    
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