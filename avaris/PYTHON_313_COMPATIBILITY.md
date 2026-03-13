# Python 3.13 Compatibility Fix for AVARIS

## Issue Description

Python 3.13 removed the deprecated `cgi` module, which is still used by some dependencies in the AVARIS project, particularly the Google Generative AI library. This causes a `ModuleNotFoundError: No module named 'cgi'` when running environment analysis.

## Solution Implemented

A compatibility shim has been added to provide the `cgi` module functionality for Python 3.13+. The fix is implemented in:

1. `main.py` - Applied at application startup
2. `backend/ai_engine/text_analyzer.py` - Applied when text analysis is used

## Compatibility Shim Details

The shim provides:
- `cgi.escape()` - Mapped to `html.escape()` (the modern replacement)
- `cgi.parse_qs()` - Stub implementation (returns empty dict)
- `cgi.parse_qsl()` - Stub implementation (returns empty list)

## Files Modified

- `main.py` - Added cgi compatibility fix at startup
- `backend/ai_engine/text_analyzer.py` - Added cgi compatibility fix for AI text generation
- `requirements.txt` - Added httpx dependency for sensor polling

## Testing

The fix has been tested with:
- Python 3.13.7
- Google Generative AI library
- Environment analysis functionality
- Text generation with Gemini API

## Verification

To verify the fix is working:

```bash
# Test basic imports
python -c "from backend.ai_engine.text_analyzer import generate_ai_text; print('Success')"

# Test analyze_environment function
python test_analyze_environment.py

# Test full backend startup
python -c "from main import app; print('Backend startup successful')"
```

## Alternative Solutions

If issues persist, consider:

1. **Downgrade to Python 3.12**: The most straightforward solution
   ```bash
   # Using pyenv
   pyenv install 3.12.7
   pyenv local 3.12.7
   ```

2. **Update Dependencies**: Check for newer versions of google-generativeai that support Python 3.13

3. **Use Virtual Environment**: Isolate dependencies
   ```bash
   python -m venv venv_312 --python=python3.12
   source venv_312/bin/activate  # Linux/Mac
   # or
   venv_312\Scripts\activate     # Windows
   ```

## Future Considerations

- Monitor google-generativeai library updates for native Python 3.13 support
- Consider migrating to alternative AI libraries if compatibility issues persist
- The compatibility shim can be removed once all dependencies support Python 3.13

## Error Messages Fixed

This fix resolves errors like:
- `ModuleNotFoundError: No module named 'cgi'`
- `Environment analysis failed: No module named 'cgi'`
- Import errors during backend startup related to cgi module