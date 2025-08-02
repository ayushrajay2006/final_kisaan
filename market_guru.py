# market_guru.py
# REVERTED TO STABLE MOCK DATA
# The live government API is currently unreliable. We are reverting to our
# simulated database to ensure the application remains stable and functional
# while we explore alternative data sources.

import logging

# We are back to using our reliable, simulated database.
MOCK_PRICE_DATABASE = {
    "tomato": {"price": 2100, "unit": "quintal", "market": "Rythu Bazar, Mehdipatnam"},
    "cotton": {"price": 7500, "unit": "quintal", "market": "Adilabad Market Yard"},
    "chilli": {"price": 15000, "unit": "quintal", "market": "Guntur Mirchi Yard"},
    "turmeric": {"price": 8200, "unit": "quintal", "market": "Nizamabad Market"},
    "wheat": {"price": 2250, "unit": "quintal", "market": "Karimnagar Market"},
    # --- Mapped to Telugu ---
    "టమోటా": {"price": 2100, "unit": "quintal", "market": "రైతు బజార్, మెహదీపట్నం"},
    "పత్తి": {"price": 7500, "unit": "quintal", "market": "ఆదిలాబాద్ మార్కెట్ యార్డ్"},
}


def get_market_price(text: str):
    """
    Analyzes the text to find a crop and returns its market price from the mock database.
    """
    text_lower = text.lower()
    
    # Simple entity extraction: find which crop the user is asking about.
    for crop in MOCK_PRICE_DATABASE.keys():
        if crop in text_lower:
            logging.info(f"Market Guru found crop: {crop}")
            price_info = MOCK_PRICE_DATABASE[crop]
            price_info["crop"] = crop 
            return {
                "status": "success",
                "data": price_info
            }
            
    logging.warning(f"Market Guru could not find a known crop in text: '{text}'")
    return {
        "status": "error",
        "message": "Sorry, I could not identify the crop you are asking about. Please try again."
    }
