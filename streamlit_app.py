import streamlit as st
import pandas as pd
import numpy as np
import re
import json
import os
from datetime import date
import plotly.express as px
import plotly.graph_objects as go

# ---------- YOUR EXISTING TOOLS & AGENT ----------
try:
    from agent import plan_trip
    from tools import (
        search_flights,
        recommend_hotel,
        find_attractions,
        get_weather_forecast,
        estimate_total_cost,
    )
except ImportError:
    # Fallback mocks in case tools not found
    plan_trip = lambda x: "Mock itinerary (tools not found)."
    class MockTool:
        def invoke(self, *args, **kwargs):
            return "Mock result ₹5000"
    search_flights = recommend_hotel = find_attractions = get_weather_forecast = estimate_total_cost = MockTool()

# ---------- LOAD FLIGHT DATA ----------
def load_flight_pairs():
    flights_path = os.path.join("data", "flights.json")
    if not os.path.exists(flights_path):
        return [], {}
    with open(flights_path, "r") as f:
        flights = json.load(f)
    pairs = {}
    for f in flights:
        fr = f.get("from")
        to = f.get("to")
        if fr and to:
            if fr not in pairs:
                pairs[fr] = set()
            pairs[fr].add(to)
    pairs = {k: sorted(v) for k, v in pairs.items()}
    sources = sorted(pairs.keys())
    return sources, pairs

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- NEON THEMES ----------
NEON_THEMES = {
    "Neon Cyan": {
        "bg_gradient": "linear-gradient(135deg, #050b14 0%, #0a192f 100%)",
        "card_bg": "rgba(10, 25, 47, 0.6)",
        "text_color": "#e6f1ff",
        "border_color": "#64ffda",
        "accent": "#64ffda",
        "accent_alt": "#00bfff",
        "glow": "0 0 12px rgba(100, 255, 218, 0.2)",
    },
    "Neon Purple": {
        "bg_gradient": "linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 100%)",
        "card_bg": "rgba(20, 10, 40, 0.7)",
        "text_color": "#f0e6ff",
        "border_color": "#bf00ff",
        "accent": "#bf00ff",
        "accent_alt": "#ff00aa",
        "glow": "0 0 12px rgba(191, 0, 255, 0.3)",
    },
    "Neon Blue": {
        "bg_gradient": "linear-gradient(135deg, #001f3f 0%, #004080 100%)",
        "card_bg": "rgba(0, 50, 100, 0.6)",
        "text_color": "#cce7ff",
        "border_color": "#1e90ff",
        "accent": "#1e90ff",
        "accent_alt": "#00bfff",
        "glow": "0 0 12px rgba(30, 144, 255, 0.3)",
    },
    "Neon Orange": {
        "bg_gradient": "linear-gradient(135deg, #2c0a00 0%, #5e2a00 100%)",
        "card_bg": "rgba(60, 30, 10, 0.6)",
        "text_color": "#ffe0b3",
        "border_color": "#ff8c00",
        "accent": "#ff8c00",
        "accent_alt": "#ffae42",
        "glow": "0 0 12px rgba(255, 140, 0, 0.3)",
    },
    "Neon Pink": {
        "bg_gradient": "linear-gradient(135deg, #2a0a1a 0%, #4a1030 100%)",
        "card_bg": "rgba(60, 20, 40, 0.6)",
        "text_color": "#ffcce6",
        "border_color": "#ff69b4",
        "accent": "#ff69b4",
        "accent_alt": "#ff1493",
        "glow": "0 0 12px rgba(255, 105, 180, 0.3)",
    },
}

def load_css(theme_name):
    theme = NEON_THEMES[theme_name]
    st.markdown(f"""
    <style>
    .stApp {{
        background: {theme["bg_gradient"]};
        background-attachment: fixed;
    }}
    html, body, [class*="css"], .stMarkdown, p, div, span, label, .stTextInput, .stSelectbox {{
        color: {theme["text_color"]} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {theme["accent"]} !important;
        font-weight: 800 !important;
        text-shadow: 0 0 5px {theme["accent"]};
    }}
    .glass-card {{
        background: {theme["card_bg"]};
        backdrop-filter: blur(12px);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid {theme["border_color"]};
        box-shadow: {theme["glow"]};
    }}
    .stButton > button {{
        background: transparent;
        color: {theme["accent"]};
        border: 2px solid {theme["accent"]};
        font-weight: bold;
        border-radius: 0.5rem;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        background: {theme["accent"]};
        color: #000 !important;
        box-shadow: 0 0 15px {theme["accent"]};
    }}
    [data-testid="stSidebar"] {{
        background: rgba(5, 10, 20, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid {theme["border_color"]};
    }}
    input, textarea, select {{
        background: rgba(0,0,0,0.5) !important;
        color: {theme["text_color"]} !important;
        border: 1px solid {theme["border_color"]} !important;
    }}
    .metric-card {{
        background: {theme["card_bg"]};
        backdrop-filter: blur(12px);
        border-radius: 1.5rem;
        padding: 1rem;
        text-align: center;
        border: 1px solid {theme["border_color"]};
        box-shadow: {theme["glow"]};
        transition: all 0.3s ease;
    }}
    .metric-value {{
        font-size: 2.5rem;
        font-weight: 800;
        color: {theme["accent"]};
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: {theme["text_color"]};
    }}
    .metric-delta {{
        font-size: 0.8rem;
        color: {theme["accent"]};
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "theme" not in st.session_state:
    st.session_state.theme = "Neon Cyan"

sources_list, pairs_dict = load_flight_pairs()
if not sources_list:
    sources_list = ["Bangalore", "Delhi", "Mumbai"]
    pairs_dict = {"Bangalore": ["Goa", "Delhi"], "Delhi": ["Goa", "Kolkata"], "Mumbai": ["Goa", "Delhi"]}

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("### 🎨 Theme Selector")
    selected_theme = st.selectbox("Interface Style", list(NEON_THEMES.keys()), index=list(NEON_THEMES.keys()).index(st.session_state.theme))
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()
    load_css(st.session_state.theme)

    st.markdown("---")
    st.header("🧳 Trip Parameters")
    source = st.selectbox("Origin Point", sources_list)
    destinations = pairs_dict.get(source, ["Goa", "Delhi"])
    destination = st.selectbox("Target Sector", destinations)
    start_date = st.date_input("Launch Date", date(2026, 6, 10))
    end_date = st.date_input("Return Date", date(2026, 6, 12))
    budget_pref = st.selectbox("Resource Allocation", ["Low", "Moderate", "Luxury"])
    interests = st.text_input("Directives (comma sep)", "beaches, heritage")

    if st.button("✨ INITIATE PLANNING", use_container_width=True):
        with st.spinner("🌍 Agent is planning your perfect trip..."):
            try:
                # Fetch tool data
                flight_res = search_flights.invoke({"source": source, "destination": destination, "date": start_date.strftime("%Y-%m-%d")})
                hotel_res = recommend_hotel.invoke({"city": destination, "min_rating": 4.0, "max_price": 5000})
                places_res = find_attractions.invoke({"city": destination, "category": interests.split(",")[0].strip() if interests else "beach"})
                weather_res = get_weather_forecast.invoke({"city": destination, "start_date": start_date.strftime("%Y-%m-%d"), "end_date": end_date.strftime("%Y-%m-%d")})

                # --- VALIDATION: stop if essential data missing ---
                if "No flights found" in flight_res:
                    st.error("❌ No direct flight available for the selected route. Please choose a different source/destination pair.")
                    st.session_state["result"] = None
                    st.stop()
                if "No hotels found" in hotel_res:
                    st.warning("⚠️ No hotels found in the destination city. The itinerary may use generic suggestions.")
                if "No attractions found" in places_res:
                    st.warning("⚠️ No attractions found. The itinerary will recommend popular spots based on your interests.")

                # Extract prices for metrics
                price_match = re.search(r'₹(\d+)', flight_res)
                flight_price = int(price_match.group(1)) if price_match else 5000
                hotel_price_match = re.search(r'₹(\d+)/night', hotel_res)
                hotel_price = int(hotel_price_match.group(1)) if hotel_price_match else 3000
                nights = (end_date - start_date).days
                budget_res = estimate_total_cost.invoke({
                    "flight_price": flight_price,
                    "hotel_price_per_night": hotel_price,
                    "nights": nights,
                    "daily_expenses": 2000
                })

                st.session_state["tool_data"] = {
                    "flight": flight_res,
                    "hotel": hotel_res,
                    "places": places_res,
                    "weather": weather_res,
                    "budget": budget_res,
                    "flight_price": flight_price,
                    "hotel_price": hotel_price,
                    "nights": nights
                }

                # --- Generate text itinerary using the LLM (only if flight exists) ---
                user_query = f"""
                Plan a trip from {source} to {destination} from {start_date} to {end_date}.
                Budget preference: {budget_pref}. Interests: {interests}.
                Use the following real data:
                Flight: {flight_res}
                Hotel: {hotel_res}
                Attractions: {places_res}
                Weather: {weather_res}
                Budget: {budget_res}
                Provide a day-wise itinerary.
                """
                result = plan_trip(user_query)
                st.session_state["result"] = result

            except Exception as e:
                st.error(f"Planning error: {e}")

# ---------- MAIN AREA HEADER ----------
st.markdown("""
<style>
.banner {
    background: linear-gradient(135deg, #0a0f2c 0%, #0d1b3e 50%, #0a0f2c 100%);
    padding: 2rem 1.5rem;
    border-radius: 1.5rem;
    margin: 1rem 0 2rem 0;
    position: relative;
    overflow: hidden;
    box-shadow: 0 0 20px #00ffcc;
    text-align: center;
}
.banner h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: white !important;
    text-shadow: 0 0 10px #00ffcc;
    margin: 0;
}
.banner .gold {
    color: #ffd700 !important;
    font-size: 1rem;
    margin-top: 0.5rem;
    letter-spacing: 2px;
}
.banner .icons {
    margin-top: 1rem;
    font-size: 1.8rem;
    display: flex;
    justify-content: center;
    gap: 1.5rem;
}
</style>
<div class="banner">
    <h1>✈️ AGENTIC AI TRAVEL PLANNER</h1>
    <div class="gold">POWERED BY LANGCHAIN & OPEN‑METEO</div>
    <div class="icons">
        <span>🗺️</span><span>✈️</span><span>🏨</span><span>🌴</span><span>🌦️</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- METRICS SECTION ----------
st.markdown("## Welcome back, **User**! 👋")
st.markdown("### AI Trip Predictions")

if st.session_state.get("tool_data"):
    data = st.session_state["tool_data"]
    flight_price = data.get("flight_price", 5000)
    hotel_price = data.get("hotel_price", 3000)
    nights = data.get("nights", 2)
    places_text = data.get("places", "")
    if "No attractions found" in places_text or not places_text:
        places_count = 0
    else:
        places_count = len(re.findall(r'^\d+\.', places_text, re.MULTILINE))
    total_budget = flight_price + (hotel_price * nights) + (2000 * nights)
    weather_text = data.get("weather", "")
    if weather_text and "Weather forecast for" in weather_text:
        lines = weather_text.split("\n")
        weather_summary = lines[1] if len(lines) > 1 else weather_text[:50]
    else:
        weather_summary = "Forecast available"
else:
    flight_price = 5000
    hotel_price = 3000
    places_count = 0
    total_budget = 15000
    weather_summary = "2026-06-10: ☀️ 32°C – 34°C"

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">₹{flight_price}</div><div class="metric-label">Flight Price</div><div class="metric-delta">Lowest fare</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">₹{hotel_price}</div><div class="metric-label">Hotel / night</div><div class="metric-delta">4★ rating</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">{places_count}</div><div class="metric-label">Attractions</div><div class="metric-delta">Top rated</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card"><div class="metric-value">₹{total_budget}</div><div class="metric-label">Total Budget</div><div class="metric-delta">Including local</div></div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class="metric-card"><div style="font-size:1.2rem; font-weight:bold; color:#00ffcc;">{weather_summary[:50]}</div><div class="metric-label">Weather</div><div class="metric-delta">Live forecast</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ---------- TEXT ITINERARY ----------
if "result" in st.session_state and st.session_state["result"]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## 📋 Your Personalized Itinerary")
    st.markdown(st.session_state["result"])
    st.markdown('</div>', unsafe_allow_html=True)
    col_dl1, col_dl2, col_dl3 = st.columns([1,2,1])
    with col_dl2:
        st.download_button(
            label="📥 Download Itinerary (TXT)",
            data=st.session_state["result"],
            file_name="trip_plan.txt",
            mime="text/plain",
            use_container_width=True
        )
else:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🌟 Welcome to your AI-powered travel companion\n\n- ✨ Get personalised day-wise itineraries\n- 🌦️ Live weather forecasts\n- 💰 Smart budget estimation\n- 🏨 Hotel & flight recommendations\n- 📊 **15 interactive 2D charts**\n\n👈 Fill in your trip details and click 'INITIATE PLANNING'")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------- 15 CHARTS SECTION (unchanged) ----------
st.markdown("## 📊 DEEP DIVE ANALYTICS OVERVIEW")
st.markdown("*Scrolling data projection sequence initiated. Each metric isolated for maximum clarity.*")

current_theme = NEON_THEMES[st.session_state.theme]
accent = current_theme["accent"]
accent_alt = current_theme["accent_alt"]
text_col = current_theme["text_color"]

def style_2d(fig, title="", height=450):
    fig.update_layout(
        title=dict(text=title, font=dict(color=accent, size=20, family="Courier New")),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_col, family="Courier New"),
        margin=dict(l=40, r=40, t=60, b=40),
        height=height,
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor=accent_alt),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)", zerolinecolor=accent_alt)
    )
    return fig

# Chart 1: Flight Price Gauge
st.markdown("<br>", unsafe_allow_html=True)
fig1 = go.Figure(go.Indicator(
    mode="gauge+number", value=flight_price, number={'prefix': "₹", 'font': {'color': accent, 'size': 50}},
    title={'text': "ESTIMATED FLIGHT PRICE", 'font': {'color': text_col, 'size': 20}},
    gauge={'axis': {'range': [None, 10000]}, 'bar': {'color': accent}, 'bgcolor': "rgba(255,255,255,0.1)"}
))
st.plotly_chart(style_2d(fig1, height=350), use_container_width=True)
st.markdown("---")

# Chart 2: Hotel Price Gauge
fig2 = go.Figure(go.Indicator(
    mode="gauge+number", value=hotel_price, number={'prefix': "₹", 'font': {'color': accent_alt, 'size': 50}},
    title={'text': "AVERAGE HOTEL / NIGHT", 'font': {'color': text_col, 'size': 20}},
    gauge={'axis': {'range': [None, 8000]}, 'bar': {'color': accent_alt}, 'bgcolor': "rgba(255,255,255,0.1)"}
))
st.plotly_chart(style_2d(fig2, height=350), use_container_width=True)
st.markdown("---")

# Chart 3: Budget Health Gauge
fig3 = go.Figure(go.Indicator(
    mode="gauge+number", value=92, number={'suffix': "%", 'font': {'color': "#00ffcc", 'size': 50}},
    title={'text': "BUDGET HEALTH SCORE", 'font': {'color': text_col, 'size': 20}},
    gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#00ffcc"}, 'bgcolor': "rgba(255,255,255,0.1)"}
))
st.plotly_chart(style_2d(fig3, height=350), use_container_width=True)
st.markdown("---")

# Chart 4: Daily Spending Donut
labels = ['Food', 'Local Travel', 'Activities', 'Miscellaneous']
values = [40, 20, 30, 10]
fig4 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, 
                              marker=dict(colors=[accent, accent_alt, "#ff00aa", "#b366ff"]))])
fig4.update_traces(hoverinfo='label+percent', textinfo='label+percent', textfont_size=16)
fig4.update_layout(showlegend=True)
st.plotly_chart(style_2d(fig4, "1. EXPECTED DAILY SPENDING BREAKDOWN", height=500), use_container_width=True)
st.markdown("---")

# Chart 5: Route Projection Map (with improved coordinates)
city_coords = {
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Goa": (15.2993, 74.1240),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Jaipur": (26.9124, 75.7873),
}
src_lat, src_lon = city_coords.get(source, (20.5937, 78.9629))
dst_lat, dst_lon = city_coords.get(destination, (20.5937, 78.9629))
df_route = pd.DataFrame([
    {"City": source, "lat": src_lat, "lon": src_lon},
    {"City": destination, "lat": dst_lat, "lon": dst_lon}
])
fig5 = px.scatter_geo(df_route, lat="lat", lon="lon", hover_name="City", text="City", projection="natural earth")
fig5.update_traces(marker=dict(size=18, color=accent, line=dict(width=2, color="white")),
                   textposition="bottom right", textfont=dict(size=14, color="white"))
fig5.add_trace(go.Scattergeo(lat=df_route["lat"], lon=df_route["lon"], mode='lines',
                             line=dict(width=4, color=accent_alt), name="Route"))
fig5.update_geos(showcountries=True, countrycolor="rgba(100, 255, 218, 0.4)",
                 showland=True, landcolor="rgba(10, 20, 40, 0.9)", showocean=True,
                 oceancolor="rgba(0, 0, 0, 0)", bgcolor="rgba(0,0,0,0)")
st.plotly_chart(style_2d(fig5, "2. ROUTE PROJECTION MAP", height=500), use_container_width=True)
st.markdown("---")

# Chart 6: Airline Scatter
df_flight_2d = pd.DataFrame({
    "Duration (Hrs)": [1.5, 1.8, 2.0, 2.5, 1.6], 
    "Price (₹)": [4200, 4800, 5500, 3900, 6000], 
    "Airline": ["SpiceJet", "IndiGo", "Vistara", "Air India Express", "Air India"]
})
fig6 = px.scatter(df_flight_2d, x="Duration (Hrs)", y="Price (₹)", color="Airline", size="Price (₹)", size_max=25)
fig6.update_traces(marker=dict(line=dict(width=1, color='White')))
st.plotly_chart(style_2d(fig6, "3. AIRLINE COMPARISON: DURATION VS PRICE", height=500), use_container_width=True)
st.markdown("---")

# Chart 7: Cumulative Budget Area
days = np.arange(1, 8)
costs = np.cumsum([flight_price, hotel_price, 2500, 1500, 3000, 1000, 500])
fig7 = px.area(x=days, y=costs, labels={'x': 'Timeline (Days)', 'y': 'Cumulative Cost (₹)'})
fig7.update_traces(line_color=accent_alt, fillcolor=f"rgba(0, 191, 255, 0.2)")
st.plotly_chart(style_2d(fig7, "4. CUMULATIVE BUDGET TRAJECTORY", height=500), use_container_width=True)
st.markdown("---")

# Chart 8: Rainfall Forecast Area
rain_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
rain_mm = [0, 0, 5, 12, 2, 0, 0]
fig8 = px.area(x=rain_days, y=rain_mm, labels={'x': 'Day of Week', 'y': 'Precipitation (mm)'})
fig8.update_traces(line_color="#ff00aa", fillcolor="rgba(255, 0, 170, 0.2)", mode='lines+markers', marker=dict(size=12))
st.plotly_chart(style_2d(fig8, "5. PRECIPITATION PROBABILITY FORECAST", height=500), use_container_width=True)
st.markdown("---")

# Chart 9: Interest Clusters Bubble
np.random.seed(42)
df_int = pd.DataFrame({
    "Rating": np.random.randint(60, 100, 30), 
    "Volume (Searches)": np.random.randint(500, 5000, 30), 
    "Category": np.random.choice(["Beach", "Heritage", "Nightlife", "Food"], 30)
})
fig9 = px.scatter(df_int, x="Rating", y="Volume (Searches)", color="Category", size="Volume (Searches)", 
                  color_discrete_sequence=[accent, accent_alt, "#ff00aa", "#b366ff"])
st.plotly_chart(style_2d(fig9, "6. DESTINATION INTEREST CLUSTERS", height=500), use_container_width=True)
st.markdown("---")

# Chart 10: Temperature Heatmap
x_days = [start_date.strftime("%b %d"), (start_date+pd.Timedelta(days=1)).strftime("%b %d"), (start_date+pd.Timedelta(days=2)).strftime("%b %d")]
y_times = ['Morning', 'Afternoon', 'Evening', 'Night']
z_temps = [[28, 29, 28], [32, 33, 31], [29, 29, 28], [26, 26, 25]]
fig10 = go.Figure(data=go.Heatmap(z=z_temps, x=x_days, y=y_times, colorscale='Tealgrn'))
st.plotly_chart(style_2d(fig10, "7. TEMPERATURE GRADIENT HEATMAP", height=500), use_container_width=True)
st.markdown("---")

# Chart 11: Flight Pricing by Hour Scatter
hours = np.random.randint(0, 24, 150)
prices = 4000 + (np.abs(hours - 12) * 150) + np.random.randint(-400, 400, 150)
fig11 = px.scatter(x=hours, y=prices, labels={'x': 'Departure Hour (24H)', 'y': 'Price (₹)'}, color=prices, color_continuous_scale='aggrnyl')
fig11.update_layout(coloraxis_showscale=False)
st.plotly_chart(style_2d(fig11, "8. FLIGHT PRICING VARIANCE BY HOUR", height=500), use_container_width=True)
st.markdown("---")

# Chart 12: Hotel Tier Bar
df_hotel_bar = pd.DataFrame({
    "Category": ["Luxury (5★)", "Premium (4★)", "Budget (3★)", "Hostel/Guest"], 
    "Average Price (₹)": [12000, 6000, 3000, 1200], 
    "User Rating": [4.8, 4.2, 3.8, 4.5]
})
fig12 = px.bar(df_hotel_bar, x="Category", y="Average Price (₹)", color="User Rating", color_continuous_scale="Purp", text="Average Price (₹)")
fig12.update_layout(coloraxis_showscale=False)
st.plotly_chart(style_2d(fig12, "9. ACCOMMODATION TIER ANALYSIS", height=500), use_container_width=True)
st.markdown("---")

# Chart 13: Hotel Star Distribution Histogram
h_stars = np.random.choice([1, 2, 3, 4, 5], 200, p=[0.05, 0.15, 0.45, 0.25, 0.10])
fig13 = px.histogram(x=h_stars, nbins=5, labels={'x': 'Star Rating Category'}, color_discrete_sequence=[accent_alt])
fig13.update_layout(bargap=0.2, xaxis=dict(tickvals=[1,2,3,4,5]))
st.plotly_chart(style_2d(fig13, "10. HOTEL STAR AVAILABILITY DISTRIBUTION", height=500), use_container_width=True)
st.markdown("---")

# Chart 14: Sentiment Radar
categories = ['Food Quality', 'Safety', 'Cost Efficiency', 'Activities', 'Transit Ease']
accent_rgb = tuple(int(accent[i:i+2], 16) for i in (1, 3, 5)) if accent.startswith('#') else (100, 255, 218)
fill_rgba = f"rgba({accent_rgb[0]}, {accent_rgb[1]}, {accent_rgb[2]}, 0.3)"
fig14 = go.Figure(data=go.Scatterpolar(r=[9, 8, 8, 10, 7], theta=categories, fill='toself',
                                       line_color=accent, fillcolor=fill_rgba))
fig14.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,0.2)")), showlegend=False)
st.plotly_chart(style_2d(fig14, "11. DESTINATION SENTIMENT RADAR", height=600), use_container_width=True)
st.markdown("---")

# Chart 15: Conversion Funnel
fig15 = go.Figure(go.Funnel(
    y=["Initial Searches", "Flights Selected", "Hotels Viewed", "Itineraries Finalized", "Trips Booked"], 
    x=[5000, 3200, 1800, 800, 350], 
    textinfo="value+percent initial",
    marker={'color': [accent, accent_alt, "#ff00aa", "#b366ff", "#00ffcc"]}
))
st.plotly_chart(style_2d(fig15, "12. USER BOOKING CONVERSION FUNNEL", height=500), use_container_width=True)

# No footer line added