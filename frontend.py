# frontend.py
# FINAL VERSION: This UI is simplified to display the natural language responses
# from the LLM brain and includes the intuitive, combined location feature.

import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- Page Setup ---
st.set_page_config(page_title="AI Farmer Assistant", page_icon="🧑‍🌾", layout="wide")
st.title("🧑‍🌾 AI Farmer Assistant")
st.markdown("Your personal AI-powered guide for modern farming.")

def ask_question(location):
    """Helper function to call the backend and display the LLM's response."""
    with st.spinner("Listening... then thinking..."):
        try:
            payload = {"language_code": "en-IN", "location": location}
            response = requests.post(f"{BACKEND_URL}/listen_and_understand", json=payload)
            response.raise_for_status()
            result = response.json()
            
            st.success("Heard you!")
            st.markdown(f"> *“{result.get('transcription')}”*")
            st.divider()
            
            # Display the natural language response from the LLM
            st.markdown(result.get("agent_response"))

        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- Main Application Sections ---
st.header("🗣️ Voice Assistant")
st.markdown("Enter your location, or allow the browser to use your current position.")

# --- Combined and Streamlined Location Input ---
location_data = streamlit_geolocation()
manual_location = st.text_input("Enter your location (e.g., city, district):", "Mumbai")

if st.button("🎤 Ask a Question"):
    final_location = ""
    if location_data and location_data.get('latitude'):
        auto_location = f"{location_data['latitude']},{location_data['longitude']}"
        st.info(f"📍 Using your current GPS location for the most accurate forecast.")
        final_location = auto_location
    elif manual_location:
        final_location = manual_location
    
    if final_location:
        ask_question(final_location)
    else:
        st.warning("Please enter a location or allow location access in your browser.")

st.divider()

# --- Crop Diagnosis Section (Unchanged) ---
st.header("🌿 Crop Disease Diagnosis")
st.write("Upload an image of a crop leaf to check for diseases.")
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image.", use_column_width=True)
    with st.spinner("Analyzing image..."):
        try:
            files = {"image": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{BACKEND_URL}/diagnose_disease", files=files)
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "success":
                data = result.get("data", {})
                st.subheader(f"Diagnosis: {data.get('disease_name')}")
                st.warning(f"**Confidence:** {data.get('confidence_score', 0)*100:.2f}%")
                st.info(f"**Recommendation:** {data.get('recommendation')}")
            else:
                st.error(result.get("message", "Failed to get a diagnosis."))
        except Exception as e:
            st.error(f"An error occurred during diagnosis: {e}")
