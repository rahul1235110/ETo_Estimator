import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

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
def calculate_aet(et_0, soil_moisture, soil_moisture_max):
    return et_0 * (soil_moisture / soil_moisture_max)

# Function to calculate irrigation requirement based on Kc value
def calculate_irrigation_requirement(et_0, kc_value):
    irrigation_requirement = et_0 * kc_value
    return irrigation_requirement

# Custom HTML + JS to fetch geolocation
def get_geolocation():
    # HTML + JS code to get geolocation
    html = """
    <script type="text/javascript">
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const location = { lat: lat, lon: lon };
                window.parent.postMessage(location, "*");
            });
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    </script>
    """
    components.html(html)

# Streamlit UI to take latitude and longitude as input
st.title("🌾 Crop Irrigation and Growth Tracker 🌦️💧")

# Option to automatically fetch the location or manually input lat and lon
use_device_location = st.checkbox("Use my device's location 📍", value=True)

if use_device_location:
    get_geolocation()

    # Once location is fetched, it will be automatically displayed by the JS code
    lat = st.number_input("Latitude", 35.0, format="%.6f")
    lon = st.number_input("Longitude", 139.0, format="%.6f")
    st.write(f"📍 Location detected: Latitude = {lat}, Longitude = {lon}")
else:
    # Manually input the latitude and longitude
    lat = st.number_input("Enter Latitude 📍", value=35.0, format="%.6f")
    lon = st.number_input("Enter Longitude 📍", value=139.0, format="%.6f")

# Crop Selection
crop_type = st.selectbox("🌱 Select Crop Type 🌾", ["Cotton", "Redgram", "Wheat", "Rice", "Corn"])

# Input for Crop Sowing Date
sowing_date = st.date_input("📅 Enter Sowing Date", datetime.today())

# Calculate Crop Growth Stage
stage, days_since_sowing = calculate_crop_stage(str(sowing_date))

st.write(f"🌱 **Crop Stage**: {stage}")
st.write(f"📅 **Days Since Sowing**: {days_since_sowing} days")

# Display Kc Values for the Selected Crop and Stage
current_kc = kc_values[crop_type]
if stage == "🌱 Initial Stage":
    kc = current_kc[0]
elif stage == "🌾 Mid-Season Stage":
    kc = current_kc[1]
else:
    kc = current_kc[2]

st.write(f"🌿 **Current Kc Value for {crop_type}**: {kc}")

# Fetch weather and soil data based on user input
weather_data = fetch_weather_data(lat, lon)
soil_data = fetch_soil_data(lat, lon)

# Process and display weather data
if weather_data:
    st.markdown("### 🌤️ **Weather Forecast Data**:")
    temp_max = kelvin_to_celsius(weather_data[0]['main']['temp_max'])

    # Calculate ET₀ using the Jensen-Haise equation
    et_0 = jensen_haise_et0(T_max=temp_max)

    st.markdown(f"🌡️ **Max Temperature (T_max):** {temp_max:.2f} °C")
    st.markdown(f"🌞 **Estimated ET₀ (from Jensen-Haise Method):** {et_0:.2f} mm/day")

# Process and display soil data
if soil_data:
    st.markdown("### 🌱 **Soil Data**:")
    soil_moisture = soil_data['moisture']  # Soil moisture from the API (as a fraction)
    st.markdown(f"💧 **Current Soil Moisture from API**: {soil_moisture * 100:.2f} %")

    soil_moisture_max = 0.50  # Example max soil moisture (field capacity)

    # Calculate AET based on soil moisture and ET₀
    aet = calculate_aet(et_0, soil_moisture, soil_moisture_max)
    st.markdown(f"💧 **Estimated AET (Actual Evapotranspiration)**: {aet:.2f} mm/day")

    # Calculate irrigation requirement based on crop stage and Kc value
    irrigation = calculate_irrigation_requirement(et_0, kc)
    st.markdown(f"💧 **Recommended Irrigation Requirement for {crop_type}**: {irrigation:.2f} mm/day")

    # Now, adjust irrigation recommendation based on soil moisture and rain forecast
    soil_moisture_example = soil_moisture
    rain_forecast = 0.0  # mm (from weather forecast API)

    # Adjust irrigation recommendation
    adjusted_irrigation = irrigation * (1 - soil_moisture_example)  # This accounts for soil moisture already present
    adjusted_irrigation = adjusted_irrigation - rain_forecast  # Subtract any rainfall expected

    st.markdown(f"🌧️ **Adjusted Irrigation Requirement (considering soil moisture and rainfall)**: {adjusted_irrigation:.2f} mm/day")
