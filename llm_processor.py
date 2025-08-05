# llm_processor.py
# CONVERSATIONAL VERSION: This is the new central brain. It uses an advanced prompt
# that understands chat history to hold a real conversation.

import logging
import requests
import json

# --- Configuration ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
API_KEY = "AIzaSyBb1SHvN8frWKXEfOZupKa27bIs0akT2gU" 

def generate_conversational_response(question: str, intent: str, chat_history: list, retrieved_data: dict):
    """
    Generates a conversational response using the LLM, considering the chat history and retrieved data.
    """

    # --- NEW CONVERSATIONAL SYSTEM PROMPT ---
    prompt = f"""
    **Your Persona:** You are an incredibly experienced and respected agricultural specialist who has worked with Indian farmers for over 30 years. You are a patient, empathetic guide who explains complex topics in simple, practical terms.

    **Your Task:** You are having a conversation with a farmer. You must provide a helpful and accurate response to their latest question, using the conversation history for context and the provided technical data for facts.

    **Rules for Your Response:**
    1.  **Be Conversational:** Acknowledge the flow of the conversation. If the farmer asks a follow-up question, use phrases like "Certainly, regarding that scheme..." or "To give you more details on that...".
    2.  **Use the Chat History:** The history is crucial for understanding context. If the farmer says "tell me more about the first one," you must look at the previous message in the history to know what "the first one" is.
    3.  **Ground Your Answers in Data:** If you are provided with "Technical Data," your answer MUST be based on that data. Do not make up information. If the data is not sufficient to answer, say "I couldn't find specific details on that in my knowledge base, but here is what I do know...". If no data is provided, answer the question to the best of your general knowledge.
    4.  **Speak Simply and Clearly:** No jargon. Explain things in a way a farmer can immediately understand and act upon.
    5.  **Be Action-Oriented and Empathetic:** Give clear advice and maintain a supportive tone.

    ---
    **Conversation History (for context):**
    ```json
    {json.dumps(chat_history, indent=2)}
    ```
    ---
    **Farmer's Latest Question:** "{question}"
    ---
    **Technical Data Retrieved by Specialist Tools (use this for your answer):**
    ```json
    {json.dumps(retrieved_data, indent=2) if retrieved_data else "No specific data was retrieved for this query."}
    ```
    ---

    Now, based on all of the above, please craft the perfect, conversational response to the farmer's latest question.
    """
    # --- END OF NEW PROMPT ---

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    full_api_url = f"{GEMINI_API_URL}?key={API_KEY}"

    try:
        logging.info("Sending data to LLM for conversational synthesis...")
        response = requests.post(full_api_url, headers=headers, json=payload, timeout=45)
        response.raise_for_status()
        result = response.json()
        
        if (result.get('candidates') and result['candidates'][0].get('content')):
            llm_response = result['candidates'][0]['content']['parts'][0]['text']
            logging.info("LLM synthesis successful.")
            return llm_response
        else:
            logging.error(f"Unexpected LLM response format: {result}")
            return "Sorry, I received an unusual response from my AI brain."

    except Exception as e:
        logging.error(f"An unexpected error occurred during LLM synthesis: {e}")
        return "An unexpected error occurred while generating the response."
