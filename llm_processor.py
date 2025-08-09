# llm_processor.py
# FINAL ADVISOR VERSION (PLURAL FIX): This version contains an upgraded prompt
# that explicitly instructs the LLM to use the singular form of a commodity name
# when calling a tool, ensuring compatibility with the rigid government API.

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
    **Your Persona:** You are an incredibly experienced and respected agricultural market advisor from India. You have a deep understanding of mandi operations and price fluctuations. Your goal is to give farmers clear, actionable advice to help them get the best price for their produce.

    **Your Task:** You are having a conversation with a farmer. Your primary goal is to answer their latest question using the provided data and context.

    **Special Instructions for Market Analysis (Intent: 'Market_Analysis'):**
    - If you need to use your market price tool, you MUST respond with ONLY a valid JSON object.
    - **CRITICAL RULE:** The 'commodity' parameter in the JSON MUST be the singular form of the crop (e.g., "tomatoes" becomes "Tomato", "apples" becomes "Apple"). This is essential for the government database.
    - Determine the location. If the question mentions a location (e.g., "in Punjab"), use that. Otherwise, you MUST use the "User's Current Location" provided.
    - Construct the JSON in the following format:
    ```json
    {{
      "tool_to_use": "market_price_api",
      "parameters": {{
        "commodity": "...",
        "state": "...",
        "district": "..."
      }}
    }}
    ```
    - If you are provided with "Technical Data" (meaning the tool has already run), analyze the data and provide a conversational answer. Acknowledge the search_scope and give a clear recommendation.

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
