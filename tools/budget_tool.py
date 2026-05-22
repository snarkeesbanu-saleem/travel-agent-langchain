from langchain.tools import tool

@tool
def estimate_total_cost(flight_price: float = 0, hotel_price_per_night: float = 0, 
                        nights: int = 1, daily_expenses: float = 2000) -> str:
    """
    Estimate total trip budget including flight, hotel, food & local travel.
    Daily expenses default ₹2000 (adjustable).
    """
    hotel_total = hotel_price_per_night * nights
    local_total = daily_expenses * nights
    total = flight_price + hotel_total + local_total
    
    breakdown = (f"💰 Budget Breakdown:\n"
                 f"   Flight: ₹{flight_price}\n"
                 f"   Hotel ({nights} nights): ₹{hotel_total}\n"
                 f"   Food & Local Travel: ₹{local_total} (₹{daily_expenses}/day)\n"
                 f"   ─────────────────────\n"
                 f"   Total Estimated Cost: ₹{total}\n")
    return breakdown