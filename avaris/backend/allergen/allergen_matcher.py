import json
import os

def load_json_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_json_db(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=1)

def match_allergens(ingredients, allergen_db_path):
    allergen_db = load_json_db(allergen_db_path)
    detected_allergens = set()
    
    ingredients_lower = [i.lower() for i in ingredients]
    
    for allergen, keywords in allergen_db.items():
        for keyword in keywords:
            for ingredient in ingredients_lower:
                if keyword.lower() in ingredient:
                    detected_allergens.add(allergen)
                    break
                    
    return list(detected_allergens)

def evaluate_risk(detected_allergens):
    count = len(detected_allergens)
    if count == 0:
        return "LOW"
    elif count == 1:
        return "MEDIUM"
    else:
        return "HIGH"

def save_to_known_foods(food_item, ingredients, known_foods_path):
    known_foods = load_json_db(known_foods_path)
    # Use food_item as key, but maybe normalized
    key = food_item.lower().strip()
    if key and key not in known_foods:
        known_foods[key] = ingredients
        save_json_db(known_foods_path, known_foods)

def get_ingredients_from_cache(food_item, known_foods_path):
    known_foods = load_json_db(known_foods_path)
    return known_foods.get(food_item.lower().strip())
