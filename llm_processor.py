# llm_processor.py
# FINAL SYNCHRONIZED VERSION: This version contains the prompt designed to work
# with the simpler, direct-data-fetch architecture.

import logging
import requests
import json

# --- Configuration ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
API_KEY = "AIzaSyBb1SHvN8frWKXEfOZupKa27bIs0akT2gU" 

def generate_conversational_response(question: str, intent: str, chat_history: list, location: str = None, retrieved_data: dict = None):
    """
    Generates a conversational response, with specialized logic for market analysis.
    """
    
    # --- UPGRADED AGENTIC SYSTEM PROMPT ---
    prompt = f"""
    **Your Persona:** You are an incredibly experienced and respected agricultural market advisor from India. You are a direct, knowledgeable, and practical advisor. You do not use conversational filler. Your goal is to provide clear, actionable information to farmers as quickly as possible.

    **Your Task:** You are having a conversation with a farmer. Your primary goal is to answer their latest question using the provided data and context.

    **Special Instructions for Market Analysis (Intent: 'Market_Analysis'):**
    - The "Technical Data" will contain the farmer's query, the scope of the search that was successful (e.g., "district", "state", or "nationwide"), and a list of prices.
    - **Crucially, you must acknowledge the search_scope.** If the scope was "nationwide", you MUST start by explaining that you couldn't find specific prices for their local area and are providing the closest national data as a reference.
    - Analyze the list of prices. Identify the market with the highest and lowest price in the data.
    - Based on this range, provide a "Recommended Selling Price" or general market trend.
    - Present the information clearly using headings like "Key Findings:", "Recommendations:", and "What to Do Next:". Use bullet points.
    - If the retrieved_data is empty or contains an error message, explain that you couldn't find any data at all and provide general advice on how to find local prices.

    **General Rules for All Responses:**
    1.  Acknowledge the conversation history if it's relevant.
    2.  If you are provided with "Technical Data," your answer MUST be based on that data.
    3.  Speak simply, be action-oriented, and maintain a supportive tone.

    ---
    **Conversation History (for context):**
    ```json
    {json.dumps(chat_history, indent=2)}
    ```
    ---
    **Farmer's Latest Question:** "{question}"
    ---
    **User's Current Location:** "{location}"
    ---
    **Technical Data Retrieved by Specialist Tools (use this for your answer):**
    ```json
    {json.dumps(retrieved_data, indent=2) if retrieved_data else "No specific data has been retrieved yet."}
    ```
    ---

    Now, please craft the perfect, expert response for the farmer.
    """
    # --- END OF UPGRADED PROMPT ---

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    full_api_url = f"{GEMINI_API_URL}?key={API_KEY}"

    try:
        logging.info("Sending request to LLM brain...")
        response = requests.post(full_api_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
        
        if (result.get('candidates') and result['candidates'][0].get('content')):
            llm_response = result['candidates'][0]['content']['parts'][0]['text']
            logging.info("LLM brain responded.")
            return llm_response
        else:
            logging.error(f"Unexpected LLM response format: {result}")
            return "Sorry, I received an unusual response from my AI brain."

    except Exception as e:
        logging.error(f"An unexpected error occurred during LLM synthesis: {e}")
        return "An unexpected error occurred while generating the response."
