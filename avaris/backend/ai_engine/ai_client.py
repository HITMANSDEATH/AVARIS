"""
Centralized AI client for AVARIS.
Single initialization point for Gemini API — all other modules import from here.
"""
import logging
import google.generativeai as genai
from backend.config.settings import settings

logger = logging.getLogger("avaris.ai")

# ── Gemini Initialization (runs once at import) ──────────────────────────────

_gemini_ready = False

def _init_gemini() -> bool:
    key = settings.GEMINI_API_KEY
    if key and key not in ("", "YOUR_API_KEY_HERE"):
        genai.configure(api_key=key)
        logger.info("Gemini API configured successfully.")
        return True
    logger.warning("Gemini API key not set — AI features will use offline fallback.")
    return False

_gemini_ready = _init_gemini()


def is_gemini_available() -> bool:
    """Check if the Gemini API is configured and ready."""
    return _gemini_ready


# ── Model Accessors ──────────────────────────────────────────────────────────

TEXT_MODEL = "gemini-2.0-flash"      # Fast and cheap — ideal for short explanations
VISION_MODEL = "gemini-2.0-flash"    # Multimodal capable

def get_text_model():
    """Return a GenerativeModel configured for text generation."""
    return genai.GenerativeModel(TEXT_MODEL)

def get_vision_model():
    """Return a GenerativeModel configured for vision tasks."""
    return genai.GenerativeModel(VISION_MODEL)


# ── Unified Generate Function ────────────────────────────────────────────────

def generate_text(prompt: str) -> str:
    """
    Generate text using Gemini if available, otherwise return an offline fallback.
    This is the single entry point for all text-based AI calls in AVARIS.
    """
    if not _gemini_ready:
        logger.warning("AI unavailable — returning static fallback response.")
        return (
            "⚠️ AI analysis unavailable (offline mode). "
            "Please review sensor readings manually."
        )

    try:
        model = get_text_model()
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini text generation failed: {e}", exc_info=True)
        return f"AI analysis error: {str(e)}. Please review manually."
