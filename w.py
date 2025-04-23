import streamlit as 
import requests
from datetime import datetime
import math

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
        st.error("Failed to fetch weather data")
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
        st.error("Failed to fetch soil data")
        return None

# Function to convert Kelvin to Celsius
def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

# Function to calculate ET₀ using the Jensen-Haise method
def jensen_haise_et0(T_max):
    return 0.025 * (T_max+273 - 2.5)

# Function to calculate AET based on soil moisture and ET₀
def calculate_aet(et_0, soil_moisture, soil_moisture_max):
    return et_0 * (soil_moisture / soil_moisture_max)

# Streamlit UI to take latitude and longitude as input
st.title("Weather and Soil Data Fetcher for ET₀ Estimation 🌦️🌍")

# Input for Latitude and Longitude
lat = st.number_input("Enter Latitude 📍", value=35.0, format="%.6f")
lon = st.number_input("Enter Longitude 📍", value=139.0, format="%.6f")

# Input for Field Capacity (max soil moisture)
soil_moisture_max = st.number_input("Enter Field Capacity (Max Soil Moisture) 💧", value=0.30, min_value=0.10, max_value=1.0, step=0.01)

# Run button to fetch and display data
if st.button('Run'):
    # Fetch data from APIs based on user input for lat and lon
    weather_data = fetch_weather_data(lat, lon)
    soil_data = fetch_soil_data(lat, lon)

    # Process and display weather data
    if weather_data:
        st.markdown("### 🌤️ **Weather Forecast Data**:")
        temp_max = kelvin_to_celsius(weather_data[0]['main']['temp_max'])
        
        # Calculate ET₀ using the Jensen-Haise equation
        et_0 = jensen_haise_et0(T_max=temp_max)
        
        st.markdown(f"**Max Temperature (T_max):** {temp_max:.2f} °C 🌡️")
        st.markdown(f"**Estimated ET₀ (from Jensen-Haise Method):** {et_0:.2f} mm/day 🌞")

        # Fetch the soil moisture from the API response (ensure soil_data is valid)
        if soil_data and 'moisture' in soil_data:
            soil_moisture = soil_data['moisture']  # Soil moisture from the API (as a fraction)
            st.markdown(f"**Current Soil Moisture from API:** {soil_moisture * 100:.2f} % 💧")
            
            # Calculate and display AET based on soil moisture
            aet = calculate_aet(et_0, soil_moisture, soil_moisture_max)
            st.markdown(f"**Estimated AET based on Soil Moisture and Field Capacity:** {aet:.2f} mm/day 💧")

    # Process and display soil data
    if soil_data:
        st.markdown("### 🌱 **Soil Data**:")
        st.markdown(f"**Soil Moisture from API:** {soil_data['moisture']} 💧")
        st.markdown(f"**Soil Temperature at 10cm:** {kelvin_to_celsius(soil_data['t10']):.2f} °C 🌡️")
        st.markdown(f"**Soil Temperature at Surface:** {kelvin_to_celsius(soil_data['t0']):.2f} °C 🌞")
