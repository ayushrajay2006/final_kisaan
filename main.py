# main.py
# FINAL VERSION: This server uses the LLM Processor to generate dynamic responses.

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional

# Import functions from all our agents
from orchestrator import listen_and_transcribe, recognize_intent
from market_guru import get_market_price
from digital_pathologist import diagnose_crop_health
from policy_advisor import get_scheme_information
from sky_watcher import get_weather_forecast
from llm_processor import generate_response

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
    version="2.0.0", # Version 2.0 with LLM Brain!
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
    
    # Step 1: Get structured data from the specialist agent (the "tool")
    intent = recognize_intent(transcribed_text, request.language_code)
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
    else: # Handle other intents or unknown cases
        final_response = "Sorry, I'm not sure how to help with that. Please try asking about weather, market prices, or government schemes."
        return { "status": "success", "transcription": transcribed_text, "agent_response": final_response }

    # Step 2: If the tool ran successfully, send its data to the LLM for synthesis
    if agent_response and agent_response.get("status") == "success":
        final_response = generate_response(
            original_question=transcribed_text,
            agent_data=agent_response['data'],
            intent=intent
        )
    else: # If the tool failed, just return its error message
        final_response = agent_response.get("message", "An unknown error occurred.")

    return {
        "status": "success",
        "transcription": transcribed_text,
        "agent_response": final_response # This is now a natural language string
    }


@app.post("/diagnose_disease")
async def handle_diagnose_disease(image: UploadFile = File(...)):
    # The disease diagnosis remains the same as it already provides a detailed response.
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded is not an image.")
    image_bytes = await image.read()
    return diagnose_crop_health(image_file_name=image.filename, image_bytes=image_bytes)
