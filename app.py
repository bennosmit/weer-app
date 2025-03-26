import streamlit as st
import requests
from datetime import datetime
import time
import folium
from streamlit_folium import folium_static
import json
import os

# API configuratie
API_KEY = st.secrets["api"]["openweathermap_api_key"]
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

# App configuratie
st.set_page_config(
    page_title="Weer App",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS voor styling
st.markdown("""
    <style>
    /* Mobile-first basis styling */
    @media (max-width: 768px) {
        .weather-card {
            margin: 10px 0;
            padding: 15px;
        }
        .metric-card {
            margin: 5px 0;
            padding: 10px;
        }
        .header {
            padding: 15px;
            margin-bottom: 20px;
        }
    }
    
    /* Algemene styling */
    .weather-card {
        background-color: white;
        border-radius: 0;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border-bottom: 1px solid #e5e5e5;
    }
    
    .header {
        text-align: left;
        padding: 20px;
        background: #0071c2;
        color: white;
        border-radius: 0;
        margin-bottom: 0;
        box-shadow: none;
    }
    
    .metric-card {
        background-color: white;
        border-radius: 0;
        padding: 15px;
        margin: 5px 0;
        text-align: left;
        box-shadow: none;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .metric-card:hover {
        background-color: #f5f5f5;
    }
    
    .favorite-city {
        display: inline-block;
        background-color: #f5f5f5;
        padding: 8px 15px;
        margin: 5px;
        border-radius: 0;
        cursor: pointer;
        transition: all 0.3s;
        border: 1px solid #e5e5e5;
        color: #333;
    }
    
    .favorite-city:hover {
        background-color: #e5e5e5;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 0;
        border: 1px solid #e5e5e5;
        padding: 10px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0071c2;
        box-shadow: none;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 0;
        background-color: #0071c2;
        color: white;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #005a9e;
    }
    
    /* Subheader styling */
    .stSubheader {
        color: #333;
        font-weight: 600;
        margin-top: 30px;
        font-size: 1.2em;
        border-bottom: 2px solid #0071c2;
        padding-bottom: 10px;
    }
    
    /* Info message styling */
    .stInfo {
        background-color: #f5f5f5;
        border: 1px solid #e5e5e5;
        border-radius: 0;
        padding: 15px;
        color: #333;
    }
    
    /* Error message styling */
    .stError {
        background-color: #fff3f3;
        border: 1px solid #ffcdd2;
        border-radius: 0;
        padding: 15px;
        color: #c62828;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #f5f5f5;
        border: 1px solid #e5e5e5;
        border-radius: 0;
        padding: 15px;
        color: #333;
    }

    /* Typography */
    h1, h2, h3 {
        font-family: "Helvetica Neue", Arial, sans-serif;
        font-weight: 600;
    }

    h1 {
        font-size: 1.8em;
        margin: 0;
    }

    h2 {
        font-size: 1.4em;
        margin: 0;
        color: #333;
    }

    h3 {
        font-size: 1.1em;
        margin: 0;
        color: #666;
    }

    p {
        font-family: "Helvetica Neue", Arial, sans-serif;
        line-height: 1.5;
        color: #333;
    }

    /* Map container */
    .folium-map {
        border: 1px solid #e5e5e5;
        margin: 20px 0;
    }

    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    .css-1d391kg .sidebar-content {
        padding: 20px;
    }

    /* Menu item styling */
    .menu-item {
        padding: 10px 15px;
        margin: 5px 0;
        cursor: pointer;
        transition: all 0.3s;
        border-left: 3px solid transparent;
    }

    .menu-item:hover {
        background-color: #e9ecef;
        border-left: 3px solid #0071c2;
    }

    .menu-item.active {
        background-color: #e9ecef;
        border-left: 3px solid #0071c2;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Functies voor favoriete steden
def load_favorites():
    if os.path.exists('favorites.json'):
        with open('favorites.json', 'r') as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    with open('favorites.json', 'w') as f:
        json.dump(favorites, f)

# Sidebar menu
with st.sidebar:
    st.markdown("""
        <div class="header">
            <h1 style="margin: 0;">🌤️ Weer App</h1>
        </div>
    """, unsafe_allow_html=True)
    
    menu_items = {
        "🏠 Home": "home",
        "🗺️ Weerkaart": "map",
        "📅 Voorspelling": "forecast",
        "⭐ Favorieten": "favorites",
        "⚙️ Instellingen": "settings"
    }
    
    selected_page = st.radio("Menu", list(menu_items.keys()), label_visibility="collapsed")

# Zoekbalk voor stad (bovenaan elke pagina)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    city = st.text_input("Voer een stad in:", "", key="city_input")

# Functies voor weergegevens
def get_weather_data(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "nl"
    }
    response = requests.get(BASE_URL, params=params)
    return response.json() if response.status_code == 200 else None

def get_forecast_data(city):
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "nl"
    }
    response = requests.get(FORECAST_URL, params=params)
    return response.json() if response.status_code == 200 else None

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def get_temperature_color(temp):
    if temp < 0:
        return "#2196F3"
    elif temp < 10:
        return "#64B5F6"
    elif temp < 20:
        return "#4CAF50"
    elif temp < 30:
        return "#FFC107"
    else:
        return "#F44336"

def format_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%H:%M')

# Pagina's
if selected_page == "🏠 Home":
    if city:
        with st.spinner("Weergegevens ophalen..."):
            data = get_weather_data(city)
            if data:
                # Weergegevens ophalen
                temp_celsius = data["main"]["temp"]
                temp_fahrenheit = celsius_to_fahrenheit(temp_celsius)
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                description = data["weather"][0]["description"]
                feels_like = data["main"]["feels_like"]
                sunrise = format_time(data["sys"]["sunrise"])
                sunset = format_time(data["sys"]["sunset"])
                current_time = datetime.fromtimestamp(data["dt"]).strftime('%d-%m-%Y %H:%M')
                
                # Stad naam weergeven
                st.markdown(f"""
                    <div class="weather-card">
                        <h2 style="text-align: center; margin-bottom: 20px;">{city.capitalize()}</h2>
                        <p style="text-align: center; color: #666;">{current_time}</p>
                """, unsafe_allow_html=True)
                
                # Weer beschrijving met emoji
                weather_emoji = {
                    "zonnig": "☀️",
                    "bewolkt": "☁️",
                    "regen": "🌧️",
                    "onweer": "⛈️",
                    "sneeuw": "🌨️",
                    "mist": "🌫️",
                    "drizzle": "🌦️",
                    "storm": "🌪️"
                }
                
                emoji = "🌤️"
                for key, value in weather_emoji.items():
                    if key in description.lower():
                        emoji = value
                        break
                
                # Weergegevens weergeven in kaarten
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-card" style="border-left: 4px solid {get_temperature_color(temp_celsius)};">
                            <h3>Temperatuur</h3>
                            <h2>{temp_celsius:.1f}°C</h2>
                            <p>Voelt als: {feels_like:.1f}°C</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>Weer</h3>
                            <h2>{emoji}</h2>
                            <p>{description.capitalize()}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>Details</h3>
                            <p>Luchtvochtigheid: {humidity}%</p>
                            <p>Windsnelheid: {wind_speed} m/s</p>
                            <p>Fahrenheit: {temp_fahrenheit:.1f}°F</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Zonsopgang en zonsondergang
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>Zonsopgang</h3>
                            <h2>🌅</h2>
                            <p>{sunrise}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card">
                            <h3>Zonsondergang</h3>
                            <h2>🌇</h2>
                            <p>{sunset}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(f"Stad niet gevonden: {city}. Controleer de spelling en probeer het opnieuw.")
    else:
        st.info("Voer een stad in om het weer te bekijken")

elif selected_page == "🗺️ Weerkaart":
    if city:
        with st.spinner("Kaart laden..."):
            data = get_weather_data(city)
            if data:
                lat = data["coord"]["lat"]
                lon = data["coord"]["lon"]
                
                st.subheader(f"Weerkaart voor {city.capitalize()}")
                m = folium.Map(location=[lat, lon], zoom_start=10)
                folium.Marker([lat, lon], popup=city).add_to(m)
                folium_static(m, width=800, height=500)
            else:
                st.error(f"Stad niet gevonden: {city}")
    else:
        st.info("Voer een stad in om de weerkaart te bekijken")

elif selected_page == "📅 Voorspelling":
    if city:
        with st.spinner("Voorspelling laden..."):
            forecast_data = get_forecast_data(city)
            if forecast_data:
                st.subheader(f"5-daagse voorspelling voor {city.capitalize()}")
                
                # Toon voorspelling per dag (om 12:00)
                daily_forecasts = []
                for item in forecast_data["list"]:
                    if item["dt_txt"].split()[1] == "12:00:00":
                        daily_forecasts.append(item)
                
                cols = st.columns(5)
                for i, forecast in enumerate(daily_forecasts[:5]):
                    date = datetime.strptime(forecast["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%d-%m")
                    temp = forecast["main"]["temp"]
                    weather = forecast["weather"][0]["description"]
                    
                    with cols[i]:
                        st.markdown(f"""
                            <div class="metric-card">
                                <h3>{date}</h3>
                                <h2>{temp:.1f}°C</h2>
                                <p>{weather.capitalize()}</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.error(f"Stad niet gevonden: {city}")
    else:
        st.info("Voer een stad in om de voorspelling te bekijken")

elif selected_page == "⭐ Favorieten":
    favorites = load_favorites()
    if favorites:
        st.subheader("Favoriete steden")
        for fav_city in favorites:
            if st.button(fav_city, key=f"fav_{fav_city}"):
                st.session_state.city_input = fav_city
                st.experimental_rerun()
    else:
        st.info("Nog geen favoriete steden toegevoegd")
    
    if city:
        if city not in favorites:
            if st.button("Toevoegen aan favorieten"):
                favorites.append(city)
                save_favorites(favorites)
                st.success(f"{city} toegevoegd aan favorieten!")
        else:
            if st.button("Verwijderen uit favorieten"):
                favorites.remove(city)
                save_favorites(favorites)
                st.success(f"{city} verwijderd uit favorieten!")

elif selected_page == "⚙️ Instellingen":
    st.subheader("App instellingen")
    st.write("Hier komen de instellingen voor de app")
