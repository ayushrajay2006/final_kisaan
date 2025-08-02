# sky_watcher.py
# This agent is now upgraded to fetch live weather data from OpenWeatherMap.

import logging
import requests

# --- Please replace this with your own API key from OpenWeatherMap ---
OPENWEATHERMAP_API_KEY = "1de6a2a410af8d6262bef94f76c2cdf1" 
OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_forecast(text: str):
    """
    Fetches a real-time weather forecast from the OpenWeatherMap API.
    It currently defaults to a fixed location (Hyderabad) but can be expanded
    to extract locations from the user's text.

    Args:
        text (str): The transcribed text from the user.

    Returns:
        dict: A dictionary containing the live weather forecast.
    """
    # For now, we'll use a default location. 
    # A future improvement would be to extract the city name from the user's text.
    location = "Hyderabad"
    logging.info(f"Sky Watcher agent fetching weather for default location: {location}")

    if OPENWEATHERMAP_API_KEY == "YOUR_API_KEY_HERE":
        logging.error("OpenWeatherMap API key is not set. Please update sky_watcher.py")
        return {
            "status": "error",
            "message": "The weather service is not configured. Missing API key."
        }

    # --- Live API Call ---
    params = {
        "q": location,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric" # To get temperature in Celsius
    }

    try:
        response = requests.get(OPENWEATHERMAP_API_URL, params=params, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()

        # Format the response into a user-friendly structure
        forecast = {
            "location": f"{data['name']}, {data['sys']['country']}",
            "temperature": f"{data['main']['temp']}°C",
            "condition": data['weather'][0]['description'].capitalize(),
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
            "alert": "No severe weather alerts at this time." # Placeholder for alert feature
        }
        
        return {
            "status": "success",
            "data": forecast
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API request failed: {e}")
        return {"status": "error", "message": "Sorry, I'm having trouble connecting to the weather service right now."}
    except KeyError:
        logging.error(f"Unexpected response format from weather API: {data}")
        return {"status": "error", "message": "Received an unexpected response from the weather service."}
    except Exception as e:
        logging.error(f"An unexpected error occurred while fetching weather: {e}")
        return {"status": "error", "message": "An unexpected error occurred while fetching the weather."}

