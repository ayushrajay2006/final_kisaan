# orchestrator.py
# This file contains the logic for our main Orchestrator Agent.
# We are now adding Intent Recognition capabilities.

import speech_recognition as sr
import logging

# Configure logging to see informational messages
logging.basicConfig(level=logging.INFO)

# --- INTENT RECOGNITION ---
# We define keywords for each intent in multiple languages.
# This simple dictionary-based approach is robust and easy to expand.
INTENT_KEYWORDS = {
    "Market_Analysis": {
        "en": ["price", "rate", "mandi", "market", "sell"],
        "hi": ["दाम", "भाव", "मंडी", "बाजार", "बेचना"],
        "te": ["ధర", "రేటు", "మండి", "మార్కెట్", "అమ్మకం"],
    },
    "Crop_Health_Diagnosis": {
        "en": ["disease", "pest", "problem", "leaf", "spot", "sick"],
        "hi": ["रोग", "कीट", "समस्या", "पत्ती", "धब्बा", "बीमार"],
        "te": ["తెగులు", "పురుగు", "సమస్య", "ఆకు", "మచ్చ", "జబ్బు"],
    },
    "Scheme_Information": {
        "en": ["scheme", "subsidy", "government", "support", "loan"],
        "hi": ["योजना", "सब्सिडी", "सरकारी", "समर्थन", "ऋण"],
        "te": ["పథకం", "సబ్సిడీ", "ప్రభుత్వ", "మద్దతు", "రుణం"],
    },
     "Weather_Forecast": {
        "en": ["weather", "rain", "hailstorm", "temperature", "forecast"],
        "hi": ["मौसम", "बारिश", "ओलावृष्टि", "तापमान", "पूर्वानुमान"],
        "te": ["వాతావరణం", "వర్షం", "వడగళ్ళు", "ఉష్ణోగ్రత", "సూచన"],
    }
}

def recognize_intent(text, language_code):
    """
    Recognizes the user's intent based on keywords in the transcribed text.

    Args:
        text (str): The transcribed text from the user.
        language_code (str): The language code (e.g., "en-IN", "hi-IN"). We use the
                             first two letters for our keyword matching (e.g., "en", "hi").

    Returns:
        str: The identified intent, or "Unknown" if no intent is found.
    """
    lang = language_code.split('-')[0] # Extract "en" from "en-IN"
    text_lower = text.lower()

    for intent, language_map in INTENT_KEYWORDS.items():
        if lang in language_map:
            for keyword in language_map[lang]:
                if keyword in text_lower:
                    logging.info(f"Found keyword '{keyword}' for intent '{intent}'")
                    return intent
    
    logging.warning(f"Could not determine intent for text: '{text}'")
    return "Unknown"

# --- SPEECH-TO-TEXT (Existing function) ---
def listen_and_transcribe(language_code="en-IN"):
    """
    Listens for audio input from the microphone and transcribes it into text
    using Google's Web Speech API.
    (This function remains unchanged from the previous step)
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        logging.info("Calibrating for ambient noise... Please be quiet.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        logging.info(f"Listening in {language_code}...")
        print("Say something!")

        try:
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            logging.info("Recognizing...")
            text = recognizer.recognize_google(audio_data, language=language_code)
            logging.info(f"Transcription: {text}")
            return {"status": "success", "transcription": text, "language": language_code}

        except sr.WaitTimeoutError:
            error_message = "No speech detected within the timeout period."
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        
        except sr.UnknownValueError:
            error_message = "Google Web Speech API could not understand the audio."
            logging.error(error_message)
            return {"status": "error", "message": error_message}

        except sr.RequestError as e:
            error_message = f"Could not request results from Google Web Speech API; {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}
        
        except Exception as e:
            error_message = f"An unexpected error occurred: {e}"
            logging.error(error_message)
            return {"status": "error", "message": error_message}