# frontend.py
# This is the user interface for our AI Farmer Assistant, built with Streamlit.

import streamlit as st
import requests
import base64 # Needed for audio playback in the future

# --- Configuration ---
# The address of our FastAPI backend
BACKEND_URL = "http://127.0.0.1:8000"

# --- Page Setup ---
st.set_page_config(
    page_title="AI Farmer Assistant",
    page_icon="🧑‍🌾",
    layout="wide"
)

st.title("🧑‍🌾 AI Farmer Assistant")
st.markdown("Your personal AI-powered guide for modern farming.")

# --- Helper Function to format agent responses ---
def display_agent_response(response_data):
    """Formats and displays the agent's response in a user-friendly way."""
    if not response_data or response_data.get("status") != "success":
        st.error(response_data.get("message", "An unknown error occurred."))
        return

    data = response_data.get("data", {})
    intent = st.session_state.get("intent", "Unknown")

    if intent == "Market_Analysis":
        st.subheader(f"📈 Market Price for {data.get('crop', 'N/A')}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Modal Price", data.get('modal_price', 'N/A'))
        col2.metric("Market", data.get('market', 'N/A'))
        col3.metric("Last Updated", data.get('date', 'N/A'))

    elif intent == "Weather_Forecast":
        st.subheader(f"🌦️ Weather Forecast for {data.get('location', 'N/A')}")
        alert_level = data.get("alert_level", "NORMAL")
        
        if alert_level == "CRITICAL":
            st.error(f"**Critical Alert:** {data.get('alert_message')}")
        elif alert_level == "HIGH":
            st.warning(f"**High Alert:** {data.get('alert_message')}")
        else:
            st.info(f"**Alert:** {data.get('alert_message')}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", data.get('temperature', 'N/A'))
        col2.metric("Condition", data.get('condition', 'N/A'))
        col3.metric("Humidity", data.get('humidity', 'N/A'))

    elif intent == "Scheme_Information":
        st.subheader(f"📜 Info on: {data.get('scheme_name', 'N/A')}")
        st.markdown(f"**Summary:** {data.get('summary')}")
        st.markdown(f"**Eligibility:** {data.get('eligibility')}")
        st.markdown(f"**Documents Needed:** {data.get('documents_needed')}")
        st.markdown(f"**How to Apply:** {data.get('how_to_apply')}")

    else:
        # Default display for other intents or errors
        st.json(response_data)


# --- Main Application Sections ---
st.header("🗣️ Voice Assistant")
st.write("Click the button and speak your question. You can ask about market prices, weather, or government schemes.")

if st.button("🎤 Ask a Question"):
    with st.spinner("Listening... Please speak into your microphone."):
        try:
            # Call the backend to listen and process
            response = requests.post(f"{BACKEND_URL}/listen_and_understand", json={"language_code": "en-IN"})
            response.raise_for_status() # Raise an exception for bad status codes
            
            result = response.json()
            st.session_state['intent'] = result.get("intent") # Store intent for formatting

            st.success("Heard you!")
            st.markdown(f"> *“{result.get('transcription')}”*")
            
            display_agent_response(result.get("agent_response"))

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend. Is it running? Error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")


st.divider()


st.header("🌿 Crop Disease Diagnosis")
st.write("Upload an image of a crop leaf to check for diseases.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
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

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to the backend. Is it running? Error: {e}")
        except Exception as e:
            st.error(f"An error occurred during diagnosis: {e}")

