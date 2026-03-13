"""
Reasoning Module for AVARIS
Provides AI-powered explanations for risks and food allergen analysis using Gemini
"""

from backend.ai_engine.text_analyzer import generate_ai_text
import logging

logger = logging.getLogger(__name__)

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
    - Dust Level: {dust} μg/m³
    
    Please provide:
    1. A brief explanation of the primary risk factor.
    2. Recommended actions to mitigate the risk immediately.
    Keep it concise and actionable.
    """
    
    try:
        return generate_ai_text(prompt)
    except Exception as e:
        logger.error(f"Error generating risk explanation: {e}")
        return _fallback_explain_risk(risk_level, temperature, humidity, dust)

def explain_food_risk(food_item: str, ingredients: list, detected_allergens: list, risk_level: str) -> str:
    """
    Generate an AI explanation for food allergen risks.
    """
    allergen_text = ', '.join(detected_allergens) if detected_allergens else 'None'
    ingredient_text = ', '.join(ingredients) if ingredients else 'Unknown'
    
    prompt = f"""
    You are AVARIS, an AI Environmental and Health Risk Monitor.
    Analyze this food report:
    - Food Item: {food_item}
    - Ingredients: {ingredient_text}
    - Detected Allergens: {allergen_text}
    - Risk Level: {risk_level}
    
    The user may be allergic to the detected allergens.
    Generate a clear, helpful safety explanation. 
    Explain why it's a risk (if any) and what the user should do.
    Keep it concise and actionable.
    """
    
    try:
        return generate_ai_text(prompt)
    except Exception as e:
        logger.error(f"Error generating food risk explanation: {e}")
        return _fallback_explain_food_risk(food_item, ingredients, detected_allergens, risk_level)

# Fallback explanations (used when Gemini is unavailable)

def _fallback_explain_risk(risk_level: str, temperature: float, humidity: float, dust: float) -> str:
    """Fallback explanation for risk levels"""
    risk_factors = []
    
    if temperature > 35 or temperature < 10:
        risk_factors.append("extreme temperature")
    if humidity > 80 or humidity < 20:
        risk_factors.append("extreme humidity")
    if dust > 75:
        risk_factors.append("high particulate matter")
    
    if risk_factors:
        primary_risk = ", ".join(risk_factors)
        explanation = f"Risk level {risk_level} due to {primary_risk}"
    else:
        explanation = f"Risk level {risk_level} detected based on environmental conditions"
    
    recommendations = []
    if temperature > 35:
        recommendations.append("improve cooling/ventilation")
    elif temperature < 10:
        recommendations.append("check heating systems")
    
    if humidity > 80:
        recommendations.append("use dehumidifiers")
    elif humidity < 20:
        recommendations.append("increase humidity levels")
    
    if dust > 75:
        recommendations.append("replace air filters and improve ventilation")
    
    if not recommendations:
        recommendations.append("monitor conditions closely and follow safety protocols")
    
    action = ", ".join(recommendations)
    return f"{explanation}. Immediate actions: {action}."

def _fallback_explain_food_risk(food_item: str, ingredients: list, detected_allergens: list, risk_level: str) -> str:
    """Fallback explanation for food risks"""
    if not detected_allergens:
        return f"No allergens detected in {food_item}. This food appears safe based on the identified ingredients: {', '.join(ingredients)}."
    
    allergen_list = ', '.join(detected_allergens)
    
    if risk_level == "HIGH":
        risk_explanation = f"HIGH RISK: Multiple allergens ({allergen_list}) detected in {food_item}"
        action = "AVOID this food completely. Seek immediate medical attention if consumed"
    elif risk_level == "MEDIUM":
        risk_explanation = f"MEDIUM RISK: Allergen ({allergen_list}) detected in {food_item}"
        action = "Exercise caution. Avoid if you have known allergies to these ingredients"
    else:
        risk_explanation = f"LOW RISK: Potential allergen traces in {food_item}"
        action = "Monitor for any allergic reactions if consumed"
    
    ingredient_info = f"Detected ingredients: {', '.join(ingredients)}"
    
    return f"{risk_explanation}. {ingredient_info}. Recommendation: {action}."
