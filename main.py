import os
import requests
from fastapi import FastAPI, Query
from dotenv import load_dotenv

load_dotenv()

AI_ML_API_KEY = os.getenv("AI_ML_API_KEY")
AI_ML_BASE_URL = os.getenv("AI_ML_BASE_URL")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

app = FastAPI(title="Climate Policy Backend")

@app.get("/")
def root():
    return {"message": "Climate Policy API is running 🚀"}

@app.get("/weather")
def get_weather(city: str = Query(..., description="City name")):
    try:
        # ---- Open Meteo ----
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        geo_data = requests.get(geo_url).json()
        if "results" not in geo_data:
            return {"error": "City not found"}
        
        lat = geo_data["results"][0]["latitude"]
        lon = geo_data["results"][0]["longitude"]

        open_meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        open_meteo_data = requests.get(open_meteo_url).json()

        # ---- WeatherAPI ----
        weatherapi_url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={city}"
        weatherapi_data = requests.get(weatherapi_url).json()

        return {
            "city": city,
            "OpenMeteo": open_meteo_data,
            "WeatherAPI": weatherapi_data
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/policy")
def generate_policy(city: str):
    weather_data = get_weather(city)
    
    headers = {
        "Authorization": f"Bearer {AI_ML_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a climate policy expert."},
            {"role": "user", "content": f"Given this weather data {weather_data}, suggest climate-friendly policies for {city}."}
        ]
    }
    gpt_response = requests.post(f"{AI_ML_BASE_URL}/chat/completions", headers=headers, json=payload).json()
    return {
        "city": city,
        "weather": weather_data,
        "policy": gpt_response["choices"][0]["message"]["content"]
    }
