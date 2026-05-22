import json
import os
from langchain.tools import tool
from typing import Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "flights.json")

@tool
def search_flights(source: str, destination: str, date: Optional[str] = None) -> str:
    """
    Find available flights from source to destination.
    Returns cheapest flight option with airline, price, and departure time.
    """
    try:
        with open(DATA_PATH, "r") as f:
            flights = json.load(f)
    except FileNotFoundError:
        return "Flight data not found. Please ensure flights.json exists in data/ folder."
    
    matches = [f for f in flights if f.get("from", "").lower() == source.lower() 
               and f.get("to", "").lower() == destination.lower()]
    
    if date:
        matches = [f for f in matches if f.get("date", "") == date]
    
    if not matches:
        return f"No flights found from {source} to {destination}."
    
    cheapest = min(matches, key=lambda x: x.get("price", float("inf")))
    airline = cheapest.get("airline", "Unknown")
    price = cheapest.get("price", 0)
    depart = cheapest.get("departure", "N/A")
    flight_no = cheapest.get("flight_number", "N/A")
    
    return (f"✈️ Flight found: {airline} {flight_no}\n"
            f"   Departure: {depart}\n"
            f"   Price: ₹{price}\n"
            f"   From {source} to {destination}")