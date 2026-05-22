import requests
from langchain.tools import tool
from datetime import datetime, timedelta

@tool
def get_weather_forecast(city: str, start_date: str = "", end_date: str = "") -> str:
    """
    Get weather forecast for a city for up to 7 days.
    Dates optional: format YYYY-MM-DD. If not provided, returns next 5 days.
    """
    # Geocoding: city name → coordinates
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en"
    try:
        geo_resp = requests.get(geo_url)
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            return f"City '{city}' not found."
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]
    except Exception as e:
        return f"Error geocoding city: {str(e)}"
    
    # Determine forecast days
    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days + 1
            days = min(days, 7)  # API max 7 days
        except:
            days = 5
    else:
        days = 5
    
    # Fetch weather
    forecast_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
        "timezone": "auto",
        "forecast_days": days
    }
    try:
        resp = requests.get(forecast_url, params=params)
        data = resp.json()
        daily = data["daily"]
    except Exception as e:
        return f"Weather API error: {str(e)}"
    
    # Simple weather code mapping
    def weather_emoji(code):
        if code == 0: return "☀️"
        if code in [1,2]: return "⛅"
        if code == 3: return "☁️"
        if code in [45,48]: return "🌫️"
        if code in [51,53,55,61,63,65,80,81,82]: return "🌧️"
        if code in [71,73,75,77]: return "❄️"
        if code >= 95: return "⛈️"
        return "🌡️"
    
    result = f"🌤️ Weather forecast for {city}:\n"
    for i in range(len(daily["time"])):
        date = daily["time"][i]
        max_t = daily["temperature_2m_max"][i]
        min_t = daily["temperature_2m_min"][i]
        rain = daily["precipitation_sum"][i]
        code = daily["weathercode"][i]
        emoji = weather_emoji(code)
        result += f"{date}: {emoji} {min_t}°C – {max_t}°C | Rain: {rain}mm\n"
    
    return result