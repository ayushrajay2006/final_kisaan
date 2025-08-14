# market_guru.py
# FINAL DEFINITIVE API VERSION: This agent uses the live data.gov.in API
# and includes all fixes for URL, date format, and pluralization,
# along with the intelligent tiered search logic.

import logging
import requests
from datetime import datetime
import os
import json

# --- Configuration ---
# The correct API resource URL
API_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
# Your personal API key
API_KEY = "579b464db66ec23bdd000001be37f38ca138469857bae7614b111000"

# We use the Gemini Flash model for fast and accurate entity extraction.
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
GEMINI_API_KEY = "AIzaSyBb1SHvN8frWKXEfOZupKa27bIs0akT2gU" 

def get_location_from_coords(lat, lon):
    """
    Uses a reverse geocoding API to find the district and state from coordinates.
    """
    # This is a placeholder for a real reverse geocoding API call
    # For now, we'll return a default to allow the tiered search to work
    logging.warning("Reverse geocoding not fully implemented, using default logic.")
    return None, None # In a real app, this would call a service

def extract_market_entities_with_llm(text: str, location: str):
    """
    Uses the Gemini LLM to extract entities from the user's question,
    intelligently using the provided location to fill in missing details.
    """
    logging.info(f"Using LLM to extract market entities from: '{text}' with location: '{location}'")
    
    prompt = f"""
    From the user's question and their provided location, extract the following entities: the agricultural commodity (crop), the state, and the district.

    **Rules:**
    1.  If the user's question explicitly mentions a location (e.g., "price of wheat in Punjab"), prioritize that location.
    2.  If the user's question does NOT mention a location (e.g., "price of wheat"), use the "User's Provided Location" to determine the state and district.
    3.  If an entity cannot be determined, respond with "N/A".
    4.  The commodity should be in English and properly capitalized (e.g., "Tomato", "Cotton").

    **Inputs:**
    - User's Question: "{text}"
    - User's Provided Location: "{location}"

    Respond with ONLY a valid JSON object in the following format:
    {{
        "commodity": "...",
        "state": "...",
        "district": "..."
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}
    }
    headers = {'Content-Type': 'application/json'}
    full_api_url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    try:
        response = requests.post(full_api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        result = response.json()
        
        if (result.get('candidates') and result['candidates'][0].get('content')):
            entities_text = result['candidates'][0]['content']['parts'][0]['text']
            entities_json = json.loads(entities_text)
            logging.info(f"LLM extracted entities: {entities_json}")
            return entities_json
        else: return None
    except Exception as e:
        logging.error(f"LLM entity extraction failed: {e}")
        return None


def get_market_price(text: str, location: str):
    """
    Analyzes text to find entities using an LLM, then performs a tiered search
    to find the most relevant price data from the live API.
    """
    entities = extract_market_entities_with_llm(text, location)
    
    if not entities or entities.get("commodity") == "N/A":
        return {"status": "error", "message": "I'm sorry, I couldn't understand which crop you're asking about."}

    commodity = entities["commodity"]
    
    # --- Definitive Plural Fix ---
    original_commodity = commodity
    if commodity.lower().endswith('oes'): # e.g., tomatoes, potatoes
        commodity = commodity[:-2]
    elif commodity.lower().endswith('s'): # e.g., apples
        commodity = commodity[:-1]
    
    if original_commodity != commodity:
        logging.info(f"Plural detected. Converted '{original_commodity}' to singular '{commodity}' for API call.")
    # --- End of Fix ---

    state = entities.get("state")
    district = entities.get("district")
    records = []
    search_scope = ""

    # Tier 1: Highly specific search (Commodity + State + District)
    if state and district and state != "N/A" and district != "N/A":
        search_scope = f"district: {district}"
        params = {"api-key": API_KEY, "format": "json", "limit": 100, "filters[commodity]": commodity, "filters[state]": state, "filters[district]": district}
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            records = response.json().get("records", [])
        except Exception: records = []

    # Tier 2: Broader search (Commodity + State) if Tier 1 failed
    if not records and state and state != "N/A":
        search_scope = f"state: {state}"
        params = {"api-key": API_KEY, "format": "json", "limit": 100, "filters[commodity]": commodity, "filters[state]": state}
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            records = response.json().get("records", [])
        except Exception: records = []

    # Tier 3: Broadest search (Commodity only) if all else fails
    if not records:
        search_scope = "nationwide"
        params = {"api-key": API_KEY, "format": "json", "limit": 100, "filters[commodity]": commodity}
        try:
            response = requests.get(API_URL, params=params, timeout=20)
            response.raise_for_status()
            records = response.json().get("records", [])
        except Exception: records = []
            
    if not records:
        return {"status": "error", "message": f"Sorry, I couldn't find any recent price data for {original_commodity}."}

    # Sort by date using the correct DD/MM/YYYY format
    records.sort(key=lambda r: datetime.strptime(r["arrival_date"], "%d/%m/%Y"), reverse=True)
    
    top_results = [{"market": r.get("market"), "district": r.get("district"), "state": r.get("state"), "modal_price": f"₹{r.get('modal_price')} per quintal", "date": r.get("arrival_date")} for r in records[:5]]
    
    final_data = {"query": entities, "search_scope": search_scope, "results": top_results}
    return {"status": "success", "data": final_data}
