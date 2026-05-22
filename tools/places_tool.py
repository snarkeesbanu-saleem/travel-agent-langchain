import json
import os
from langchain.tools import tool

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "places.json")

@tool
def find_attractions(city: str, category: str = "", limit: int = 5) -> str:
    """
    Find tourist attractions/places to visit in a city.
    Optionally filter by category (e.g., beach, temple, museum, heritage).
    """
    try:
        with open(DATA_PATH, "r") as f:
            places = json.load(f)
    except FileNotFoundError:
        return f"Places data file not found at {DATA_PATH}. Please ensure places.json exists."
    
    # Case‑insensitive city matching
    city_matches = [p for p in places if p.get("city", "").lower() == city.lower()]
    
    if not city_matches:
        return f"No attractions found for city: {city}."
    
    # Apply category filter if provided
    if category:
        cat_lower = category.lower()
        filtered = [p for p in city_matches 
                    if cat_lower in p.get("category", "").lower() 
                    or cat_lower in p.get("type", "").lower()]
        if not filtered:
            # Fallback: return top attractions without category filter
            sorted_all = sorted(city_matches, key=lambda x: x.get("rating", 0), reverse=True)[:limit]
            result = f"📍 No attractions matched '{category}' in {city}. Showing top attractions instead:\n"
            for i, p in enumerate(sorted_all, 1):
                rating = p.get("rating", "N/A")
                place_type = p.get("type", p.get("category", "attraction"))
                result += f"{i}. {p.get('name', 'Unknown')} – {place_type} (⭐ {rating})\n"
            return result
        else:
            matches = filtered
    else:
        matches = city_matches
    
    # Sort by rating descending
    sorted_places = sorted(matches, key=lambda x: x.get("rating", 0), reverse=True)[:limit]
    
    result = f"📍 Top attractions in {city}:\n"
    for i, p in enumerate(sorted_places, 1):
        rating = p.get("rating", "N/A")
        place_type = p.get("type", p.get("category", "attraction"))
        result += f"{i}. {p.get('name', 'Unknown')} – {place_type} (⭐ {rating})\n"
    return result