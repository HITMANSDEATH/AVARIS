"""
Allergen Checker Module
Matches ingredients against allergen database and calculates risk levels
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

class AllergenChecker:
    """Checks ingredients against allergen database"""
    
    def __init__(self, allergen_db_path: str = "database/allergen_db.json"):
        self.allergen_db_path = allergen_db_path
        self.allergen_db = self._load_allergen_db()
    
    def _load_allergen_db(self) -> dict:
        """Load the allergen database"""
        try:
            if os.path.exists(self.allergen_db_path):
                with open(self.allergen_db_path, 'r') as f:
                    db = json.load(f)
                logger.info(f"Loaded allergen database with {len(db)} allergens")
                return db
            else:
                logger.warning(f"Allergen database not found at {self.allergen_db_path}")
                return self._create_default_allergen_db()
        except Exception as e:
            logger.error(f"Error loading allergen database: {e}")
            return self._create_default_allergen_db()
    
    def _create_default_allergen_db(self) -> dict:
        """Create a default allergen database"""
        default_db = {
            "gluten": ["wheat", "flour", "bread", "pasta", "barley", "rye", "oats"],
            "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "lactose"],
            "eggs": ["egg", "eggs", "mayonnaise"],
            "nuts": ["nuts", "almond", "walnut", "cashew", "pecan", "hazelnut"],
            "peanuts": ["peanut", "peanuts", "groundnut"],
            "soy": ["soy", "soybean", "tofu", "soy sauce"],
            "fish": ["fish", "salmon", "tuna", "cod", "mackerel"],
            "shellfish": ["shrimp", "crab", "lobster", "oyster", "clam", "mussel"],
            "sesame": ["sesame", "tahini"],
            "sulfites": ["wine", "dried fruit", "processed meat"]
        }
        
        # Save default allergen database
        try:
            os.makedirs(os.path.dirname(self.allergen_db_path), exist_ok=True)
            with open(self.allergen_db_path, 'w') as f:
                json.dump(default_db, f, indent=2)
            logger.info("Created default allergen database")
        except Exception as e:
            logger.error(f"Error saving default allergen database: {e}")
        
        return default_db
    
    def check_allergens(self, ingredients: list) -> list:
        """
        Check ingredients against allergen database
        
        Args:
            ingredients (list): List of ingredients to check
            
        Returns:
            list: List of detected allergens
        """
        if not ingredients:
            return []
        
        detected_allergens = set()
        ingredients_lower = [ingredient.lower().strip() for ingredient in ingredients]
        
        for allergen, allergen_keywords in self.allergen_db.items():
            for keyword in allergen_keywords:
                keyword_lower = keyword.lower()
                for ingredient in ingredients_lower:
                    if keyword_lower in ingredient or ingredient in keyword_lower:
                        detected_allergens.add(allergen)
                        logger.info(f"Detected allergen '{allergen}' from ingredient '{ingredient}'")
                        break
        
        return list(detected_allergens)
    
    def calculate_risk_level(self, detected_allergens: list) -> str:
        """
        Calculate risk level based on number of detected allergens
        
        Args:
            detected_allergens (list): List of detected allergens
            
        Returns:
            str: Risk level (LOW, MEDIUM, HIGH)
        """
        count = len(detected_allergens)
        
        if count == 0:
            risk_level = "LOW"
        elif count == 1:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        logger.info(f"Risk level: {risk_level} ({count} allergens detected)")
        return risk_level

# Global checker instance
_allergen_checker = None

def get_allergen_checker() -> AllergenChecker:
    """Get the global allergen checker instance"""
    global _allergen_checker
    if _allergen_checker is None:
        _allergen_checker = AllergenChecker()
    return _allergen_checker

def check_ingredients_for_allergens(ingredients: list) -> tuple:
    """
    Convenience function to check ingredients for allergens
    
    Args:
        ingredients (list): List of ingredients to check
        
    Returns:
        tuple: (detected_allergens, risk_level)
    """
    checker = get_allergen_checker()
    detected_allergens = checker.check_allergens(ingredients)
    risk_level = checker.calculate_risk_level(detected_allergens)
    return detected_allergens, risk_level