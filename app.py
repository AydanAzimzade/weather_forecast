import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ---------- 1. Page setup ----------
st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("🌦️ City Weather Dashboard")
st.write("Live data from the Open-Meteo API. Use the sidebar to change the city and the time period.")

# ---------- 2. Cities we can choose from ----------
cities = {
    "New York": (40.7128, -74.0060),
    "London": (51.5074, -0.1278),
    "Tokyo": (35.6762, 139.6503),
}


# ---------- 3. Function that gets the data from the API ----------
@st.cache_data
def get_weather(lat, lon, days):
    """Download daily weather for one location and return a DataFrame."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto",
        "past_days": days,
        "forecast_days": 1,
    }
    response = requests.get(url, params)
    data = response.json()
    df = pd.DataFrame(data["daily"])
    df["time"] = pd.to_datetime(df["time"])
    return df


# ---------- 4. Sidebar controls (the interactive part) ----------
st.sidebar.header("Filters")
city = st.sidebar.selectbox("Choose a city", list(cities.keys()))
days = st.sidebar.slider("Number of past days", min_value=7, max_value=90, value=30)
metric = st.sidebar.radio(
    "Variable for the trend chart",
    ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"],
)

# ---------- 5. Get the data for the chosen city ----------
lat, lon = cities[city]
df = get_weather(lat, lon, days)

# ---------- 6. KPI cards (summary numbers) ----------
col1, col2, col3 = st.columns(3)
col1.metric("Average max temp", f"{df['temperature_2m_max'].mean():.1f} °C")
col2.metric("Total rain", f"{df['precipitation_sum'].sum():.1f} mm")
col3.metric("Rainy days", int((df["precipitation_sum"] > 0).sum()))

# ---------- 7. Charts ----------
fig_line = px.line(df, x="time", y=metric, markers=True,
                   title=f"{metric} in {city} (last {days} days)")
st.plotly_chart(fig_line)

left, right = st.columns(2)

fig_bar = px.bar(df, x="time", y="precipitation_sum", title="Daily precipitation (mm)")
left.plotly_chart(fig_bar)

fig_scatter = px.scatter(df, x="temperature_2m_max", y="wind_speed_10m_max",
                         hover_data=["time"], title="Max temperature vs. wind speed")
right.plotly_chart(fig_scatter)

# ---------- 8. Raw data table ----------
with st.expander("Show raw data"):
    st.dataframe(df)
