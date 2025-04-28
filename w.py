import streamlit as st
import requests
from datetime import datetime
import math
from streamlit_js_eval import streamlit_js_eval

# Crop Kc values (for example purposes, you can add more crops and their values)
kc_values = {
    "Cotton": [0.3, 1.15, 0.45],  # [Initial, Mid-Season, Late-Season]
    "Redgram": [0.3, 1.2, 0.5],
    "Wheat": [0.3, 1.15, 0.45],
    "Rice": [0.3, 1.2, 0.5],
    "Corn": [0.3, 1.15, 0.6],
}

# Function to calculate crop growth stage based on sowing date
def calculate_crop_stage(sowing_date):
    today = datetime.now()
    sowing_date = datetime.strptime(sowing_date, "%Y-%m-%d")
    days_since_sowing = (today - sowing_date).days

    if days_since_sowing < 30:
        stage = "🌱 Initial Stage"
    elif 30 <= days_since_sowing < 70:
        stage = "🌾 Mid-Season Stage"
    else:
        stage = "🌿 Late-Season Stage"
    return stage, days_since_sowing

# Function to fetch weather data
def fetch_weather_data(lat, lon):
    weather_url = "http://api.agromonitoring.com/agro/1.0/weather/forecast"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': '71fc994579e122b13072be4dc2e06eb7'
    }
    response = requests.get(weather_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ Failed to fetch weather data")
        return None

# Function to fetch soil data using lat and lon
def fetch_soil_data(lat, lon):
    soil_url = "http://api.agromonitoring.com/agro/1.0/soil"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': '71fc994579e122b13072be4dc2e06eb7'
    }
    response = requests.get(soil_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("⚠️ Failed to fetch soil data")
        return None

# Function to convert Kelvin to Celsius
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

# Function to calculate ET₀ using the Jensen-Haise method
def jensen_haise_et0(T_max):
    return 0.025 * (T_max + 273 - 2.5)

# Function to calculate AET based on soil moisture and ET₀
def calculate_aet(et_0, soil_moisture, soil_moisture_max, pwp):
    # If soil moisture is less than PWP, AET is zero
    if soil_moisture < pwp:
        return 0
    else:
        return et_0 * (soil_moisture / soil_moisture_max)

# Function to calculate irrigation requirement based on Kc value
def calculate_irrigation_requirement(et_0, kc_value):
    irrigation_requirement = et_0 * kc_value
    return irrigation_requirement

# Streamlit UI to take latitude and longitude as input
st.title("🌾 Crop Irrigation and Growth Tracker 🌦️💧")

# Use the streamlit_js_eval component to fetch the user's location
if st.button('Get My Location'):
    # Run the JavaScript code to get the location
    location = streamlit_js_eval('navigator.geolocation.getCurrentPosition(function(position){ return {latitude: position.coords.latitude, longitude: position.coords.longitude}; });')

    if location != "No Location Info":
        lat = location['latitude']
        lon = location['longitude']
        st.write(f"📍 Location detected: Latitude = {lat}, Longitude = {lon}")
    else:
        st.warning("❌ Please allow access to your device's location.")

# Option to enter location manually if geolocation fails
else:
    lat = st.number_input("Enter Latitude 📍", value=35.0, format="%.6f")
    lon = st.number_input("Enter Longitude 📍", value=139.0, format="%.6f")

# Input for Max Water Holding Capacity (Field Capacity)
field_capacity = st.number_input(
    "💧 Enter Max Water Holding Capacity (Field Capacity) as a fraction (e.g., 0.50 for 50%)",
    value=0.50,
    min_value=0.10,
    max_value=1.0,
    step=0.01
)

# Crop Selection
crop_type = st.selectbox("🌱 Select Crop Type 🌾", ["Cotton", "Redgram", "Wheat", "Rice", "Corn"])

# Input for Crop Sowing Date
sowing_date = st.date_input("📅 Enter Sowing Date", datetime.today())

# Calculate Crop Growth
