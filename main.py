# main.py
# FINAL CLEANED VERSION

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional

# Import functions from all our agents
from orchestrator import listen_and_transcribe, recognize_intent
from market_guru import get_market_price
from digital_pathologist import diagnose_crop_health
from policy_advisor import get_scheme_information
from sky_watcher import get_weather_forecast

# --- Pre-flight Check for Microphone ---
try:
    import speech_recognition as sr
    sr.Microphone()
except (ImportError, OSError):
    print("\n--- MICROPHONE NOT FOUND or PyAudio not installed ---\n")
# --- End of Pre-flight Check ---


app = FastAPI(
    title="AI Farmer Assistant API",
    description="An AI-powered assistant to help farmers with pricing, crop diseases, and government schemes.",
    version="1.4.0", # Version bump for live model
)

class ListenRequest(BaseModel):
    language_code: str = "en-IN"
    location: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Farmer Assistant! The server is running."}


@app.post("/listen_and_understand")
def handle_listen_and_understand(request: ListenRequest):
    transcription_result = listen_and_transcribe(language_code=request.language_code)
    if transcription_result["status"] == "error":
        raise HTTPException(status_code=400, detail=transcription_result["message"])
    
    transcribed_text = transcription_result["transcription"]
    language_code = transcription_result["language"]
    intent = recognize_intent(transcribed_text, language_code)
    
    agent_response = None
    if intent == "Market_Analysis":
        agent_response = get_market_price(transcribed_text)
    elif intent == "Scheme_Information":
        agent_response = get_scheme_information(transcribed_text)
    elif intent == "Weather_Forecast":
        if not request.location:
            agent_response = {"status": "error", "message": "Please enter a location to get a weather forecast."}
        else:
            agent_response = get_weather_forecast(location=request.location)
    elif intent == "Crop_Health_Diagnosis":
        agent_response = {"status": "info", "message": "Please use the 'Crop Disease Diagnosis' section to upload an image."}
    else:
        agent_response = {"status": "info", "message": "Could not determine a specific action for your request."}

    return {
        "status": "success",
        "transcription": transcribed_text,
        "language": language_code,
        "intent": intent,
        "agent_response": agent_response
    }


@app.post("/diagnose_disease")
async def handle_diagnose_disease(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded is not an image.")
        
    image_bytes = await image.read()
    
    diagnosis_result = diagnose_crop_health(
        image_file_name=image.filename,
        image_bytes=image_bytes
    )
    return diagnosis_result
