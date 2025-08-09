# market_guru.py
# FINAL INTELLIGENT VERSION: This agent now uses reverse geocoding to determine
# the user's district and state from their GPS coordinates, enabling hyper-local searches.

import logging
import requests
from datetime import datetime
import os
import json

# --- Configuration ---
API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
API_KEY = "579b464db66ec23bdd000001be37f38ca138469857bae7614b111000"
# We will use a free reverse geocoding API
REVERSE_GEOCODING_API_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
GEMINI_API_KEY = "AIzaSyBb1SHvN8frWKXEfOZupKa27bIs0akT2gU" 

def get_location_from_coords(lat, lon):
    """
    Uses a reverse geocoding API to find the district and state from coordinates.
    """
    params = {"latitude": lat, "longitude": lon, "localityLanguage": "en"}
    try:
        logging.info(f"Performing reverse geocoding for lat:{lat}, lon:{lon}")
        response = requests.get(REVERSE_GEOCODING_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        # The API provides various administrative levels, we'll look for district and state
        district = data.get("locality") or data.get("city")
        state = data.get("principalSubdivision")
        logging.info(f"Reverse geocoding successful: District='{district}', State='{state}'")
        return district, state
    except Exception as e:
        logging.error(f"Reverse geocoding failed: {e}")
        return None, None

def extract_commodity_with_llm(text: str):
    """Uses the LLM to extract only the crop name from the user's question."""
    prompt = f"From the following text, extract only the name of the agricultural commodity. Respond with ONLY the name of the commodity in English, capitalized. Text: \"{text}\""
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    full_api_url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    try:
        response = requests.post(full_api_url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        if (result.get('candidates') and result['candidates'][0].get('content')):
            return result['candidates'][0]['content']['parts'][0]['text'].strip()
        return None
    except Exception:
        return None

def get_market_price(text: str, location: str):
    """
    Performs a tiered search for market prices using the user's location.
    """
    commodity = extract_commodity_with_llm(text)
    if not commodity:
        return {"status": "error", "message": "I'm sorry, I couldn't understand which crop you're asking about."}

    district, state = None, None
    # Check if the location is coordinates or a name
    if ',' in location:
        try:
            lat, lon = location.split(',')
            district, state = get_location_from_coords(lat, lon)
        except ValueError:
            # It's likely a city name, use it directly
            district = location
    else:
        district = location

    # --- Tiered Search Logic ---
    records = []
    search_scope = ""
    
    # Tier 1: Search by District if available
    if district:
        search_scope = f"district: {district}"
        params = {"api-key": API_KEY, "format": "json", "limit": 100, "filters[commodity]": commodity, "filters[district]": district}
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            records = response.json().get("records", [])
        except Exception: records = []

    # Tier 2: Search by State if Tier 1 failed and state is known
    if not records and state:
        search_scope = f"state: {state}"
        params = {"api-key": API_KEY, "format": "json", "limit": 100, "filters[commodity]": commodity, "filters[state]": state}
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            records = response.json().get("records", [])
        except Exception: records = []

    # Tier 3: Nationwide search as a final fallback
    if not records:
        search_scope = "nationwide"
        params = {"api-key": API_KEY, "format": "json", "limit": 100, "filters[commodity]": commodity}
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            records = response.json().get("records", [])
        except Exception: records = []
            
    if not records:
        return {"status": "error", "message": f"Sorry, I couldn't find any recent price data for {commodity}."}

    records.sort(key=lambda r: datetime.strptime(r["arrival_date"], "%d/%m/%Y"), reverse=True)
    
    top_results = [{"market": r.get("market"), "district": r.get("district"), "state": r.get("state"), "modal_price": f"₹{r.get('modal_price')} per quintal", "date": r.get("arrival_date")} for r in records[:5]]
    
    final_data = {"query": {"commodity": commodity, "location": location}, "search_scope": search_scope, "results": top_results}
    return {"status": "success", "data": final_data}
