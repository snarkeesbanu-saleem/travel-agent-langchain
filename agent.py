import os
import re
import math
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import (
    search_flights,
    recommend_hotel,
    find_attractions,
    get_weather_forecast,
    estimate_total_cost,
)

# Store the built-in print function
_builtin_print = print

def safe_print(*args, **kwargs):
    try:
        _builtin_print(*args, **kwargs)
    except UnicodeEncodeError:
        try:
            encoding = sys.stdout.encoding or "cp1252"
            clean_args = [
                str(arg).encode(encoding, errors="replace").decode(encoding)
                for arg in args
            ]
            _builtin_print(*clean_args, **kwargs)
        except Exception:
            pass
    except Exception:
        pass

# Override global print for safe unicode printing in terminals
print = safe_print

# Load environment variables
load_dotenv()

# ----- HARDCODE YOUR GROQ API KEY -----
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
if not GROQ_API_KEY:
    # Try reading from grok.txt as fallback
    try:
        grok_path = os.path.join(os.path.dirname(__file__), "grok.txt")
        if os.path.exists(grok_path):
            with open(grok_path, "r") as f:
                GROQ_API_KEY = f.read().strip()
        else:
            grok_path_parent = os.path.join(os.path.dirname(__file__), "..", "grok.txt")
            if os.path.exists(grok_path_parent):
                with open(grok_path_parent, "r") as f:
                    GROQ_API_KEY = f.read().strip()
    except Exception:
        pass

def plan_trip(
    user_query: str,
    source: str = None,
    dest: str = None,
    start_date: str = None,
    end_date: str = None,
    budget_pref: str = None,
    interests: str = None,
    num_travelers: int = 1,
    travel_style: str = "Solo"
) -> str:
    print("=" * 50)
    print("USER QUERY:", user_query)
    print("=" * 50)

    # --- Parameter Extraction for CLI/Standalone compatibility ---
    if not source or not dest:
        route_match = re.search(r"(?:from|of)\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s+from|\s+on|\s+between|\.|$)", user_query, re.IGNORECASE)
        if route_match:
            source = source or route_match.group(1).strip()
            dest = dest or route_match.group(2).strip()
        else:
            # Check simple substrings
            if "delhi" in user_query.lower():
                source = source or "Delhi"
            if "goa" in user_query.lower():
                dest = dest or "Goa"
            source = source or "Delhi"
            dest = dest or "Goa"

    if not start_date or not end_date:
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", user_query)
        if len(dates) >= 2:
            start_date = start_date or dates[0]
            end_date = end_date or dates[1]
        elif len(dates) == 1:
            start_date = start_date or dates[0]
            try:
                from datetime import datetime, timedelta
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_date = end_date or (start_dt + timedelta(days=2)).strftime("%Y-%m-%d")
            except:
                end_date = end_date or "2026-06-12"
        else:
            start_date = start_date or "2026-06-10"
            end_date = end_date or "2026-06-12"

    if not budget_pref:
        budget_match = re.search(r"budget\s*(?:preference)?\s*[:\s-]*\s*(low|moderate|luxury|economy|premium|high)", user_query, re.IGNORECASE)
        if budget_match:
            budget_pref = budget_match.group(1).strip().capitalize()
        else:
            budget_pref = "Moderate"

    if not interests:
        interests_match = re.search(r"(?:interests|prefer|directives)\s*[:\s-]*\s*([A-Za-z\s,]+)(?:\.|$)", user_query, re.IGNORECASE)
        if interests_match:
            interests = interests_match.group(1).strip()
        else:
            interests = "beaches, heritage"

    # Calculate nights
    try:
        from datetime import datetime
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        nights = (end_dt - start_dt).days
        if nights <= 0:
            nights = 1
    except Exception:
        nights = 2

    print(f"\nTrip Parameters: {source} -> {dest} | Dates: {start_date} to {end_date} ({nights} nights) | Budget: {budget_pref} | Travelers: {num_travelers}")

    print("\n--- STEP 1: SEARCH FLIGHTS ---")
    flight_result = search_flights.invoke({"source": source, "destination": dest, "date": start_date})
    print(flight_result)

    print("\n--- STEP 2: RECOMMEND HOTEL ---")
    max_price = 3000 if budget_pref.lower() == "low" else (8000 if budget_pref.lower() == "moderate" else 999999)
    hotel_result = recommend_hotel.invoke({"city": dest, "min_rating": 4.0, "max_price": max_price})
    print(hotel_result)

    print("\n--- STEP 3: FIND ATTRACTIONS ---")
    category = interests.split(",")[0].strip() if interests else "beach"
    places_result = find_attractions.invoke({"city": dest, "category": category})
    print(places_result)

    print("\n--- STEP 4: GET WEATHER ---")
    weather_result = get_weather_forecast.invoke({"city": dest, "start_date": start_date, "end_date": end_date})
    print(weather_result)

    print("\n--- STEP 5: ESTIMATE BUDGET ---")
    # Extract flight price from result string
    price_match = re.search(r'₹(\d+)', flight_result)
    flight_price = int(price_match.group(1)) if price_match else 5000
    hotel_price_match = re.search(r'₹(\d+)/night', hotel_result)
    hotel_price = int(hotel_price_match.group(1)) if hotel_price_match else 3000
    
    # Scale budget parameters based on group size
    room_count = math.ceil(num_travelers / 2.0)
    daily_expenses_base = 1500 if budget_pref.lower() == "low" else (3500 if budget_pref.lower() == "luxury" else 2000)
    
    budget_result = estimate_total_cost.invoke({
        "flight_price": flight_price * num_travelers,
        "hotel_price_per_night": hotel_price * room_count,
        "nights": nights,
        "daily_expenses": daily_expenses_base * num_travelers
    })
    print(budget_result)

    # --- 6. Use LLM to generate final itinerary ---
    print("\n--- GENERATING FINAL ITINERARY ---")
    if not GROQ_API_KEY:
        return (f"⚠️ Groq API Key not configured. Here is the raw planning data:\n\n"
                f"**Flight:**\n{flight_result}\n\n"
                f"**Hotel:**\n{hotel_result}\n\n"
                f"**Attractions:**\n{places_result}\n\n"
                f"**Weather:**\n{weather_result}\n\n"
                f"**Estimated Cost:**\n{budget_result}")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        groq_api_key=GROQ_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert travel planner. Combine the real flight, hotel, attractions, weather, and budget data below into a clear, day-wise travel itinerary."),
        ("human", f"""
User request: {user_query}

Trip Details:
- Origin: {source}
- Destination: {dest}
- Dates: {start_date} to {end_date} ({nights} nights)
- Travelers: {num_travelers} ({travel_style} style)
- Budget Preference: {budget_pref}

Real-time API & Database Data:
Flight details:
{flight_result}

Hotel details:
{hotel_result}

Attraction details:
{places_result}

Weather details:
{weather_result}

Estimated Budget details:
{budget_result}

Please create a final travel plan with:
- Selected Flight (airline, flight number, departure, price scaled for {num_travelers} travelers)
- Recommended Hotel (name, rating, total cost for {nights} nights across {room_count} rooms)
- Day-wise itinerary (Day 1, Day 2, Day 3...) with specific activity recommendations matching interests: {interests}
- Weather expectations and suggested packing tips
- Total budget breakdown

Make it friendly, structured, beautiful (using clean Markdown styling), and detailed.
""")
    ])

    chain = prompt | llm | StrOutputParser()
    final_output = chain.invoke({})
    return final_output

if __name__ == "__main__":
    query = "Plan a 3-day trip from Delhi to Goa from 2026-06-10 to 2026-06-12. Budget moderate, prefer beach activities."
    result = plan_trip(query)
    print("\n" + "="*50)
    print("FINAL ITINERARY")
    print("="*50)
    print(result)