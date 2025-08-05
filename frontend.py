# frontend.py
# FINAL CONVERSATIONAL VERSION: This UI now supports both text input via the
# chat box and voice input via a dedicated "Speak" button.

import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- Page Setup ---
st.set_page_config(page_title="AI Farmer Assistant", page_icon="🧑‍🌾", layout="wide")
st.title("🧑‍🌾 AI Farmer Assistant")
st.markdown("Your personal AI-powered guide for modern farming.")

# --- Initialize Session State for Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Namaste! How can I help you today? You can type your question below or use the 'Speak' button."}]

# --- Location Component ---
st.sidebar.header("📍 Your Location")
st.sidebar.markdown("For accurate weather forecasts, please provide your location.")
location_data = streamlit_geolocation()
manual_location = st.sidebar.text_input("Enter City or Lat,Lon", "Mumbai")
final_location = manual_location
if location_data and location_data.get('latitude'):
    final_location = f"{location_data['latitude']},{location_data['longitude']}"
    st.sidebar.success(f"Using GPS Location: {final_location}")

# --- Helper function to process and display a question ---
def process_and_display_question(question_text):
    # Add user's message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": question_text})
    with st.chat_message("user"):
        st.markdown(question_text)

    # Call the backend with the new question and the entire chat history
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "location": final_location,
                    "question": question_text,
                    "chat_history": st.session_state.messages[:-1]
                }
                response = requests.post(f"{BACKEND_URL}/chat", json=payload)
                response.raise_for_status()
                result = response.json()
                
                full_response = result.get("agent_response")
                st.markdown(full_response)
                
                # Add AI's response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"An error occurred: {e}")

# --- Main Chat Interface ---
st.header("💬 Chat with your Assistant")

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Combined Voice and Text Input ---
# The text input for typing
if prompt := st.chat_input("Type your question here..."):
    process_and_display_question(prompt)

# The button for speaking
if st.button("🎤 Speak your question"):
    with st.spinner("Listening..."):
        try:
            # Call the new /transcribe endpoint
            response = requests.post(f"{BACKEND_URL}/transcribe")
            response.raise_for_status()
            result = response.json()
            transcribed_text = result.get("transcription")
            
            if transcribed_text:
                # If transcription is successful, process it like typed text
                process_and_display_question(transcribed_text)
            else:
                st.warning("Could not understand audio. Please try again.")
        except Exception as e:
            st.error(f"An error occurred with voice input: {e}")


# --- Crop Diagnosis Section (Sidebar) ---
st.sidebar.divider()
st.sidebar.header("🌿 Crop Disease Diagnosis")
uploaded_file = st.sidebar.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.sidebar.image(uploaded_file, caption="Uploaded Image.")
    with st.spinner("Analyzing image..."):
        try:
            files = {"image": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(f"{BACKEND_URL}/diagnose_disease", files=files)
            response.raise_for_status()
            result = response.json()
            if result.get("status") == "success":
                data = result.get("data", {})
                st.sidebar.subheader(f"Diagnosis: {data.get('disease_name')}")
                st.sidebar.warning(f"**Confidence:** {data.get('confidence_score', 0)*100:.2f}%")
                st.sidebar.info(f"**Recommendation:** {data.get('recommendation')}")
            else:
                st.sidebar.error(result.get("message", "Failed to get a diagnosis."))
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")
