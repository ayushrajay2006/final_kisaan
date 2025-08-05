# main.py
# FINAL CONVERSATIONAL VERSION: This server now has a dedicated /chat endpoint
# for text and a new /transcribe endpoint to support voice input.

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict

# Import functions from all our agents
from orchestrator import recognize_intent, listen_and_transcribe # Re-added listen_and_transcribe
from market_guru import get_market_price
from digital_pathologist import diagnose_crop_health
from policy_advisor import get_scheme_information
from sky_watcher import get_weather_forecast
from llm_processor import generate_conversational_response

app = FastAPI(
    title="AI Farmer Assistant API",
    description="A conversational AI assistant for farmers.",
    version="3.1.0", # Version bump for Voice & Text
)

# Pydantic model for chat requests
class ChatRequest(BaseModel):
    language_code: str = "en-IN"
    location: Optional[str] = None
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []

# --- NEW ENDPOINT FOR VOICE TRANSCRIPTION ---
@app.post("/transcribe")
def handle_transcribe():
    """Listens to the microphone and returns the transcribed text."""
    transcription_result = listen_and_transcribe(language_code="en-IN")
    if transcription_result["status"] == "error":
        raise HTTPException(status_code=400, detail=transcription_result["message"])
    return {"transcription": transcription_result["transcription"]}
# --- END NEW ENDPOINT ---


@app.post("/chat")
def handle_chat(request: ChatRequest):
    intent = recognize_intent(request.question, request.language_code)
    agent_data = None
    
    if intent == "Market_Analysis":
        agent_response = get_market_price(request.question)
        if agent_response.get("status") == "success": agent_data = agent_response['data']
    elif intent == "Scheme_Information":
        agent_data = get_scheme_information(request.question, request.chat_history)
    elif intent == "Weather_Forecast":
        if not request.location:
            return {"agent_response": "To give you a weather forecast, I need a location. Please provide one."}
        agent_response = get_weather_forecast(location=request.location)
        if agent_response.get("status") == "success": agent_data = agent_response['data']
    
    final_response = generate_conversational_response(
        question=request.question,
        intent=intent,
        chat_history=request.chat_history,
        retrieved_data=agent_data
    )
    return {"agent_response": final_response}


@app.post("/diagnose_disease")
async def handle_diagnose_disease(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded is not an image.")
    image_bytes = await image.read()
    return diagnose_crop_health(image_file_name=image.filename, image_bytes=image_bytes)
