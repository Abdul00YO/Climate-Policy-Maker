import os
import requests
from fastapi import FastAPI, Query
from dotenv import load_dotenv

load_dotenv()

AI_ML_API_KEY = os.getenv("AI_ML_API_KEY")
AI_ML_BASE_URL = os.getenv("AI_ML_BASE_URL")
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY")

app = FastAPI(title="Climate Policy Backend")

with open("policy_template.txt", "r", encoding="utf-8") as f:
    policy_template = f.read()

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

        open_meteo_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        )
        open_meteo_data = requests.get(open_meteo_url).json()

        # ---- WeatherAPI ----
        weatherapi_url = f"http://api.weatherapi.com/v1/current.json?key={WEATHERAPI_KEY}&q={city}"
        weatherapi_data = requests.get(weatherapi_url).json()

        return {
            "city": city,
            "OpenMeteo": open_meteo_data,
            "WeatherAPI": weatherapi_data,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/policy")
def generate_policy(
    city: str,
    user_prompt: str = Query(..., description="User prompt for policy generation"),
    model: str = Query("gpt-4o-mini", description="AI model"),
    temperature: float = Query(0.4, description="Creativity level (0-1)")
):
    weather_data = get_weather(city)

    # Guard: reject non-climate prompts
    if not any(
        word in user_prompt.lower()
        for word in ["climate", "weather", "environment", "sustainability", "policy", "green", "energy", "emission", "carbon", "pollution", "temperature", "precipitation", "flood", "drought"]
    ):
        return {"message": "❌ This model is designed for climate-related problems. Please provide a climate-related prompt."}

    headers = {
        "Authorization": f"Bearer {AI_ML_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": "You are a climate policy expert."},
            {"role": "user", "content": f"{user_prompt}\n\nHere is weather data for {city}: {weather_data} \n\nPlease provide a detailed climate policy response according to this template \n\n {policy_template}"},
        ],
    }

    gpt_response = requests.post(
        f"{AI_ML_BASE_URL}/chat/completions", headers=headers, json=payload
    ).json()

    return {
        "city": city,
        "weather": weather_data,
        "policy": gpt_response["choices"][0]["message"]["content"],
    }
