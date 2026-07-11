# ✈️ Agentic AI Travel Planner

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://travel-agent-langchain-cubkrlattdxqsgsftxa894.streamlit.app/)

**Live Demo (Streamlit Cloud)**: [https://travel-agent-langchain-cubkrlattdxqsgsftxa894.streamlit.app/](https://travel-agent-langchain-cubkrlattdxqsgsftxa894.streamlit.app/)

A premium, neon-themed **Agentic AI Travel Planner** built using **LangChain**, **Streamlit**, **Plotly**, and **Open-Meteo**. The application utilizes the **Llama-3.3-70b-versatile** model on Groq to gather flight pricing, recommend local hotels, find targeted attractions, fetch live weather forecasts, and synthesize custom day-wise travel itineraries.

---

## 🌟 Key Features

1. **Fix: Correct Planning Accuracy**:
   - Resolved the static query parsing issue. UI inputs (Origin, Destination, Dates, Budget, Interests) are now fed directly to the LangChain Agent, preventing it from defaulting to hardcoded paths.
2. **Traveler Profiles & Budget Scaling**:
   - Added Group Size and Travel Style inputs.
   - Automatically scales budget metrics, metric cards, and all Plotly analytics charts (Daily spending donut, Cumulative budget trajectory, and Accommodation tier analysis) to match group size (calculating double sharing room requirements).
3. **🎒 Dynamic Packing Checklist**:
   - Automatically generates packing checklists in the sidebar, adapting dynamically to target sector weather forecasts and interests (e.g., swimwear for beaches, modest clothing for heritage temples, umbrellas for rainy forecasts).
4. **💱 Currency Converter**:
   - Added a built-in widget in the sidebar to convert budget figures from INR (₹) to USD ($), EUR (€), GBP (£), and AED (Dirham).
5. **🎨 Custom Neon Visual Assets**:
   - Integrated custom neon-style illustrations for application banners and destination covers (Goa, Delhi, Mumbai, Bangalore) that load dynamically in the sidebar based on selection.

---

## 🛠️ Tech Stack
- **Core**: Python 3.12, Streamlit
- **LLM Orchestration**: LangChain, LangChain Groq (`Llama-3.3-70b-versatile`)
- **Analytics**: Plotly Express, Plotly Graph Objects, Pandas, NumPy
- **APIs**: Open-Meteo Geocoding and Weather Forecast API

---

## ⚙️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/snarkeesbanu-saleem/travel-agent-langchain.git
   cd travel-agent-langchain
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Credentials**:
   Create a `.env` file in the root directory and add your Groq API Key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *(The agent will automatically fall back to reading from `grok.txt` if `.env` is missing).*

---

## 🚀 Running the Application

### Streamlit Web Interface (Recommended)
Launch the interactive web application locally:
```bash
streamlit run streamlit_app.py
```
Open `http://localhost:8501` in your browser.

### Standalone CLI Agent Run
Run the agent directly from the command line:
```bash
python agent.py
```
*(Windows users running PowerShell/CMD do not need to worry about encoding exceptions; output logs print emojis safely).*

---
