# main.py
# This version adds print statements to the main delegation logic to solve the final bug.

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel

# Import functions from all our agents
from orchestrator import listen_and_transcribe, recognize_intent
from market_guru import get_market_price
from digital_pathologist import diagnose_crop_health
from policy_advisor import get_scheme_information
from sky_watcher import get_weather_forecast

# --- Pre-flight Check for Microphone (Unchanged) ---
try:
    import speech_recognition as sr
    sr.Microphone()
except ImportError:
    print("PyAudio is not installed. Please install it with 'pip install PyAudio'")
except OSError:
    print("\n--- MICROPHONE NOT FOUND ---\nThis application requires a microphone.\nPlease ensure a microphone is connected and configured.\n")
# --- End of Pre-flight Check ---


app = FastAPI(
    title="AI Farmer Assistant API",
    description="An AI-powered assistant to help farmers with pricing, crop diseases, and government schemes.",
    version="0.6.1", # Version bump for debugging!
)

class ListenRequest(BaseModel):
    language_code: str = "en-IN"

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Farmer Assistant! The server is running."}


@app.post("/listen_and_understand")
def handle_listen_and_understand(request: ListenRequest):
    """
    Handles the voice-based interaction workflow.
    """
    print("\n--- New Request Received ---") # <<< DEBUG PRINT
    
    # Step 1: Listen and Transcribe
    transcription_result = listen_and_transcribe(language_code=request.language_code)
    if transcription_result["status"] == "error":
        raise HTTPException(status_code=400, detail=transcription_result["message"])
    
    transcribed_text = transcription_result["transcription"]
    language_code = transcription_result["language"]
    
    # Step 2: Recognize Intent
    intent = recognize_intent(transcribed_text, language_code)
    
    # --- NEW DEBUGGING PRINTS ---
    print(f">>> Intent recognized as: '{intent}'")
    print(">>> Entering delegation logic...")
    # --- END OF DEBUGGING PRINTS ---

    agent_response = None
    if intent == "Market_Analysis":
        print(">>> Delegating to Market Guru...") # <<< DEBUG PRINT
        agent_response = get_market_price(transcribed_text)
    elif intent == "Scheme_Information":
        print(">>> Delegating to Policy Advisor...") # <<< DEBUG PRINT
        agent_response = get_scheme_information(transcribed_text)
    elif intent == "Weather_Forecast":
        print(">>> Delegating to Sky Watcher...") # <<< DEBUG PRINT
        agent_response = get_weather_forecast(transcribed_text)
    elif intent == "Crop_Health_Diagnosis":
        print(">>> Responding with placeholder for Crop Health.") # <<< DEBUG PRINT
        agent_response = {"status": "info", "message": "Crop health agent is not yet implemented for voice. Please use the /diagnose_disease endpoint to upload an image."}
    else:
        print(">>> Intent was Unknown or unhandled.") # <<< DEBUG PRINT
        agent_response = {"status": "info", "message": "Could not determine a specific action for your request."}
    
    print("--- Request Processing Complete ---") # <<< DEBUG PRINT
    return {
        "status": "success",
        "transcription": transcribed_text,
        "language": language_code,
        "intent": intent,
        "agent_response": agent_response
    }


@app.post("/diagnose_disease")
async def handle_diagnose_disease(image: UploadFile = File(...)):
    """
    Accepts an image upload and passes it to the Digital Pathologist agent.
    (This function is unchanged)
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded is not an image.")
        
    diagnosis_result = diagnose_crop_health(
        image_file_name=image.filename,
        image_content_type=image.content_type
    )
    return diagnosis_result
