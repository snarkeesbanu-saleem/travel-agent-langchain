import json
import os
from langchain.tools import tool

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "hotels.json")

@tool
def recommend_hotel(city: str, min_rating: float = 0, max_price: float = 999999) -> str:
    """
    Recommend hotels in a given city based on star rating and price.
    Returns top 3 hotels sorted by stars (highest first).
    """
    try:
        with open(DATA_PATH, "r") as f:
            hotels = json.load(f)
    except FileNotFoundError:
        return f"Hotel data file not found at {DATA_PATH}. Please ensure hotels.json exists in the data/ folder."
    
    # Debug: print city and number of hotels (remove in production)
    print(f"Searching hotels in city: {city}, min_stars={min_rating}, max_price={max_price}")
    
    matches = []
    for h in hotels:
        h_city = h.get("city", "").strip()
        if h_city.lower() == city.lower():
            stars = h.get("stars", 0)
            price = h.get("price_per_night", 0)
            if stars >= min_rating and price <= max_price:
                matches.append(h)
    
    if not matches:
        # Fallback: return any hotel in the city (ignore min_rating and max_price)
        fallback = [h for h in hotels if h.get("city", "").lower() == city.lower()]
        if fallback:
            # Sort by stars desc
            fallback_sorted = sorted(fallback, key=lambda x: x.get("stars", 0), reverse=True)[:3]
            result = f"🏨 No hotels matched your exact criteria, but here are available hotels in {city}:\n"
            for i, h in enumerate(fallback_sorted, 1):
                result += f"{i}. {h.get('name', 'Unknown')} – {h.get('stars', 0)}★, ₹{h.get('price_per_night', 0)}/night\n"
            return result
        else:
            return f"No hotels found in {city} at all. Please check the city name or add hotel data."
    
    # Sort by stars desc, then price asc
    sorted_hotels = sorted(matches, key=lambda x: (-x.get("stars", 0), x.get("price_per_night", 0)))[:3]
    
    result = f"🏨 Top hotel recommendations in {city}:\n"
    for i, h in enumerate(sorted_hotels, 1):
        result += f"{i}. {h.get('name', 'Unknown')} – {h.get('stars', 0)}★, ₹{h.get('price_per_night', 0)}/night\n"
    return result