import os
import re
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

# ----- HARDCODE YOUR GROQ API KEY -----
GROQ_API_KEY = "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"

def plan_trip(user_query: str) -> str:
    print("=" * 50)
    print("USER QUERY:", user_query)
    print("=" * 50)

    # --- Simple extraction (enhance as needed) ---
    source = "Delhi"
    dest = "Goa"
    start_date = "2026-06-10"
    end_date = "2026-06-12"
    if "delhi" in user_query.lower():
        source = "Delhi"
    if "goa" in user_query.lower():
        dest = "Goa"

    print("\n--- STEP 1: SEARCH FLIGHTS ---")
    flight_result = search_flights.invoke({"source": source, "destination": dest, "date": start_date})
    print(flight_result)

    print("\n--- STEP 2: RECOMMEND HOTEL ---")
    hotel_result = recommend_hotel.invoke({"city": dest, "min_rating": 4.0, "max_price": 5000})
    print(hotel_result)

    print("\n--- STEP 3: FIND ATTRACTIONS ---")
    places_result = find_attractions.invoke({"city": dest, "category": "beach"})
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
    budget_result = estimate_total_cost.invoke({
        "flight_price": flight_price,
        "hotel_price_per_night": hotel_price,
        "nights": 2,
        "daily_expenses": 2000
    })
    print(budget_result)

    # --- 6. Use LLM to generate final itinerary ---
    print("\n--- GENERATING FINAL ITINERARY ---")
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        groq_api_key=GROQ_API_KEY
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a travel planner. Combine the information below into a clear, day-wise itinerary."),
        ("human", f"""
User request: {user_query}

Flight information:
{flight_result}

Hotel recommendation:
{hotel_result}

Attractions:
{places_result}

Weather forecast:
{weather_result}

Budget:
{budget_result}

Please create a final travel plan for a 3-day trip with:
- Flight selected
- Hotel booked
- Day 1 itinerary
- Day 2 itinerary  
- Day 3 itinerary
- Weather expectations
- Total budget

Make it friendly and detailed.
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