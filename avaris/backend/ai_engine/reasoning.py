from .ai_model_switcher import explain_with_ai

def explain_anomaly(temperature: float, humidity: float, dust: float) -> str:
    """
    Generate an AI explanation for a detected anomaly based on sensor readings.
    """
    prompt = f"""
    You are AVARIS, an AI Environmental Risk Monitor. 
    An anomaly was detected with the following indoor environmental readings:
    - Temperature: {temperature} °C
    - Humidity: {humidity} %
    - Dust Level: {dust} ug/m3
    
    Please provide:
    1. A brief explanation of why these readings are anomalous.
    2. A short recommended safety action.
    Keep it concise.
    """
    return explain_with_ai(prompt)

def explain_risk(risk_level: str, temperature: float, humidity: float, dust: float) -> str:
    """
    Generate an AI explanation for high/critical risk levels.
    """
    prompt = f"""
    You are AVARIS, an AI Environmental Risk Monitor. 
    The current environment risk level is {risk_level}.
    Current readings:
    - Temperature: {temperature} °C
    - Humidity: {humidity} %
    - Dust Level: {dust} ug/m3
    
    Please provide:
    1. A brief explanation of the primary risk factor.
    2. Recommended actions to mitigate the risk immediately.
    Keep it concise.
    """
    return explain_with_ai(prompt)
def explain_food_risk(food_item: str, ingredients: list, detected_allergens: list, risk_level: str) -> str:
    """
    Generate an AI explanation for food allergen risks.
    """
    prompt = f"""
    You are AVARIS, an AI Environmental and Health Risk Monitor.
    Analyze this food report:
    - Food Item: {food_item}
    - Ingredients: {', '.join(ingredients)}
    - Detected Allergens: {', '.join(detected_allergens) if detected_allergens else 'None'}
    - Risk Level: {risk_level}
    
    The user is allergic to the detected allergens.
    Generate a clear, helpful safety explanation. 
    Explain why it's a risk and what the user should do.
    Keep it concise.
    """
    return explain_with_ai(prompt)
