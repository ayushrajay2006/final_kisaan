# frontend.py
# FINAL CORRECTED VERSION: This version sends the correct JSON payload to the backend,
# fixing the 422 Unprocessable Content error permanently.

import streamlit as st
import requests

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- Page Setup ---
st.set_page_config(
    page_title="AI Farmer Assistant",
    page_icon="🧑‍🌾",
    layout="wide"
)

st.title("🧑‍🌾 AI Farmer Assistant")
st.markdown("Your personal AI-powered guide for modern farming.")

# --- Helper Function to display agent responses ---
def display_agent_response(response_data):
    if not response_data or response_data.get("status") != "success":
        st.error(response_data.get("message", "An unknown error occurred."))
        return

    data = response_data.get("data", {})
    intent = st.session_state.get("intent", "Unknown")

    if intent == "Weather_Forecast":
        st.subheader(f"🌦️ Farming Outlook for {data.get('location', 'N/A')}")
        today = data.get('today_summary', {})
        st.info(f"**Today's Snapshot:** {today.get('condition')} with a current temperature of {today.get('temperature')}.")
        outlook = data.get('farming_outlook', {})
        st.markdown(f"**Overall Summary for the Next 3 Days:** {outlook.get('overall_summary')}")
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("##### 💧 Irrigation Advice")
            for item in outlook.get('irrigation_advice', []): st.text(f"• {item}")
        with col2:
            st.markdown("##### 💨 Spraying Advice")
            for item in outlook.get('spraying_advice', []): st.text(f"• {item}")
        with col3:
            st.markdown("##### 🚜 Field Work Advice")
            for item in outlook.get('field_work_advice', []): st.text(f"• {item}")
    
    elif intent == "Market_Analysis":
        st.subheader(f"📈 Market Price for {data.get('crop', 'N/A')}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Modal Price", data.get('modal_price', 'N/A'))
        col2.metric("Market", data.get('market', 'N/A'))
        col3.metric("Last Updated", data.get('date', 'N/A'))

    elif intent == "Scheme_Information":
        st.subheader(f"📜 Info on: {data.get('scheme_name', 'N/A')}")
        st.markdown(f"**Summary:** {data.get('summary')}")
        st.markdown(f"**Eligibility:** {data.get('eligibility')}")
        st.markdown(f"**Documents Needed:** {data.get('documents_needed')}")
        st.markdown(f"**How to Apply:** {data.get('how_to_apply')}")

    else:
        st.json(response_data)


# --- Main Application Sections ---
st.header("🗣️ Voice Assistant")
st.write("Click the button and speak your question. You can ask about market prices, weather, or government schemes.")

if st.button("🎤 Ask a Question"):
    with st.spinner("Listening... Please speak into your microphone."):
        try:
            # --- THE FIX ---
            # We now send a JSON payload with the language code, which the backend expects.
            payload = {"language_code": "en-IN"}
            response = requests.post(f"{BACKEND_URL}/listen_and_understand", json=payload)
            # --- END OF FIX ---
            
            response.raise_for_status()
            result = response.json()
            st.session_state['intent'] = result.get("intent")
            st.success("Heard you!")
            st.markdown(f"> *“{result.get('transcription')}”*")
            display_agent_response(result.get("agent_response"))
        except requests.exceptions.HTTPError as e:
            st.error(f"An HTTP error occurred: {e.response.status_code} {e.response.reason}")
            st.error(f"Details: {e.response.text}")
        except Exception as e:
            st.error(f"An error occurred: {e}")

st.divider()

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
