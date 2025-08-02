# sky_watcher.py
# FINAL LIVE VERSION: This agent uses the robust and reliable WeatherAPI.com service.

import logging
import requests
from datetime import datetime

# --- New Configuration for WeatherAPI.com ---
API_URL = "http://api.weatherapi.com/v1/forecast.json"
# --- Please replace this with your new key from WeatherAPI.com ---
API_KEY = "2cb7c56a4dda47d08ee142237250208"

LOCATION = "Hyderabad"

def analyze_and_advise(forecast_days):
    """
    Analyzes a 3-day forecast from WeatherAPI.com to generate a comprehensive farming outlook.
    """
    outlook = {
        "overall_summary": "",
        "irrigation_advice": [],
        "spraying_advice": [],
        "field_work_advice": []
    }
    
    total_precip_3_days = sum(day['day']['totalprecip_mm'] for day in forecast_days)
    avg_temp_3_days = sum(day['day']['maxtemp_c'] for day in forecast_days) / len(forecast_days)
    
    if total_precip_3_days > 20:
        outlook["overall_summary"] = "Wet week ahead. Focus on drainage and indoor tasks. High risk of fungal diseases."
    elif avg_temp_3_days > 35 and total_precip_3_days < 5:
        outlook["overall_summary"] = "Hot and dry conditions expected. High water stress on crops is likely. Prioritize irrigation."
    else:
        outlook["overall_summary"] = "Stable weather conditions expected. Good opportunity for field work and planting."

    for i, day_data in enumerate(forecast_days, 1):
        day_info = day_data['day']
        wind_speed = day_info['maxwind_kph']
        precipitation = day_info['totalprecip_mm']
        max_temp = day_info['maxtemp_c']
        
        if max_temp > 32 and precipitation < 2:
            outlook["irrigation_advice"].append(f"Day {i}: Hot and dry. Plan to irrigate, especially for young plants.")
        if precipitation > 5:
            outlook["spraying_advice"].append(f"Day {i}: Rain expected. Avoid spraying to prevent runoff.")
        elif wind_speed > 30:
            outlook["spraying_advice"].append(f"Day {i}: High winds expected. Avoid spraying to prevent drift.")
        if precipitation > 10:
            outlook["field_work_advice"].append(f"Day {i}: Unsuitable for field work due to rain.")
        elif max_temp > 20 and precipitation < 5:
             outlook["field_work_advice"].append(f"Day {i}: Good conditions for planting and other field work.")

    if not outlook["irrigation_advice"]: outlook["irrigation_advice"].append("Monitor crop needs; no critical irrigation alerts.")
    if not outlook["spraying_advice"]: outlook["spraying_advice"].append("Good conditions for spraying if needed.")
    if not outlook["field_work_advice"]: outlook["field_work_advice"].append("Conditions are suitable for general field work.")

    for key in outlook:
        if isinstance(outlook[key], list): outlook[key] = list(dict.fromkeys(outlook[key]))
    return outlook


def get_weather_forecast(text: str):
    if API_KEY == "YOUR_API_KEY_HERE":
        return {"status": "error", "message": "The weather service is not configured. Please add your API key from WeatherAPI.com."}

    params = { "key": API_KEY, "q": LOCATION, "days": 3, "aqi": "no", "alerts": "no" }

    try:
        response = requests.get(API_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        forecast_days = data.get("forecast", {}).get("forecastday", [])
        if not forecast_days:
            return {"status": "error", "message": "Could not retrieve forecast data from the weather service."}

        current_conditions = data.get("current", {})
        today_summary = {
            "condition": current_conditions.get("condition", {}).get("text", "N/A"),
            "temperature": f"{current_conditions.get('temp_c')}°C"
        }
        farming_outlook = analyze_and_advise(forecast_days)
        
        return {
            "status": "success",
            "data": {
                "location": data.get("location", {}).get("name"),
                "today_summary": today_summary,
                "farming_outlook": farming_outlook
            }
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API request failed: {e}")
        return {"status": "error", "message": "Sorry, I'm having trouble connecting to the weather service right now."}
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching weather: {e}")
        return {"status": "error", "message": "An unexpected error occurred."}
