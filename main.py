# main.py
# FINAL SYNCHRONIZED VERSION: This server uses the simpler, direct-data-fetch
# architecture that you preferred.

from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List, Dict

# Import functions from all our agents
from orchestrator import recognize_intent, listen_and_transcribe
from market_guru import get_market_price
from digital_pathologist import diagnose_crop_health
from policy_advisor import get_scheme_information
from sky_watcher import get_weather_forecast
from llm_processor import generate_conversational_response

app = FastAPI(
    title="AI Farmer Assistant API",
    description="A conversational AI assistant for farmers.",
    version="3.6.0", # Version bump for architecture revert
)

class ChatRequest(BaseModel):
    language_code: str = "en-IN"
    location: Optional[str] = None
    question: str
    chat_history: Optional[List[Dict[str, str]]] = []

@app.post("/transcribe")
def handle_transcribe():
    transcription_result = listen_and_transcribe(language_code="en-IN")
    if transcription_result["status"] == "error":
        raise HTTPException(status_code=400, detail=transcription_result["message"])
    return {"transcription": transcription_result["transcription"]}

@app.post("/chat")
def handle_chat(request: ChatRequest):
    intent = recognize_intent(request.question, request.language_code)
    
    agent_data = None
    agent_response = None
    
    if intent == "Market_Analysis":
        if not request.location:
            return {"agent_response": "To give you local market prices, I need a location. Please provide one."}
        agent_response = get_market_price(text=request.question, location=request.location)
        if agent_response.get("status") == "success":
            agent_data = agent_response['data']
    
    elif intent == "Scheme_Information":
        agent_data = get_scheme_information(request.question, request.chat_history)
    elif intent == "Weather_Forecast":
        if not request.location:
            return {"agent_response": "To give you a weather forecast, I need a location."}
        agent_response = get_weather_forecast(location=request.location)
        if agent_response.get("status") == "success": 
            agent_data = agent_response['data']
    
    # Generate the final conversational response
    final_response = generate_conversational_response(
        question=request.question,
        intent=intent,
        chat_history=request.chat_history,
        location=request.location,
        retrieved_data=agent_data
    )
    
    # If the tool failed, the agent_response will contain an error message
    if agent_response and agent_response.get("status") == "error":
        final_response = agent_response.get("message")

    return {"agent_response": final_response}

@app.post("/diagnose_disease")
async def handle_diagnose_disease(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded is not an image.")
    image_bytes = await image.read()
    return diagnose_crop_health(image_file_name=image.filename, image_bytes=image_bytes)
