# llm_processor.py
# FINAL VERSION: This is the central brain of the application, featuring the
# powerful and empathetic system prompt to generate expert, yet simple, advice.

import logging
import requests
import json

# --- Configuration ---
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
# The API key is an empty string because it will be provided by the execution environment.
# This is the correct and final implementation.
API_KEY = "AIzaSyBb1SHvN8frWKXEfOZupKa27bIs0akT2gU" 

def generate_response(original_question: str, agent_data: dict, intent: str):
    """
    Takes raw data from a specialist agent and generates a natural language response using an LLM.
    """
    
    # --- The Powerful System Prompt ---
    prompt = f"""
    **Your Persona:** You are an incredibly experienced and respected agricultural specialist who has worked directly with farmers in the fields of India for over 30 years. You are known for your deep knowledge and, more importantly, for your ability to explain complex topics in a simple, practical, and encouraging way. You are like a trusted guide and friend.

    **Your Task:** A farmer has asked a question. Your specialist tools have provided you with the raw technical data below. Your job is to synthesize this data into a genuinely helpful, easy-to-understand response that directly answers the farmer's question.

    **Rules for Your Response:**
    1.  **Speak Simply and Clearly:** Do not use technical jargon. If you must use a term like "crop lodging," immediately explain what it means in a simple way (e.g., "when strong winds push the crops over").
    2.  **Be Action-Oriented:** Don't just report the data. Tell the farmer what it *means* for them and what they should *do* about it. Give clear, step-by-step advice.
    3.  **Be Empathetic and Encouraging:** Use a positive and supportive tone. Acknowledge the farmer's hard work. Start your response with a friendly greeting like "Namaste," or "Here is the information you asked for,".
    4.  **Focus on the "Why":** Briefly explain *why* you are giving a piece of advice. For example, instead of just "Avoid spraying," say "It's best to avoid spraying before the rain, so the product doesn't wash away, which would waste your time and money."
    5.  **Be Concise:** Get straight to the most important points. Use bullet points or numbered lists to make the advice easy to read.

    ---
    **Farmer's Original Question:** "{original_question}"
    ---
    **Raw Technical Data from Specialist Agent:**
    ```json
    {json.dumps(agent_data, indent=2)}
    ```
    ---

    Now, based on all of the above, please craft the perfect response for the farmer.
    """
    # --- End of Prompt ---

    # Prepare the payload for the Gemini API
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    headers = {'Content-Type': 'application/json'}
    full_api_url = f"{GEMINI_API_URL}?key={API_KEY}"

    # Make the API call
    try:
        logging.info("Sending data to LLM for synthesis...")
        response = requests.post(full_api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the generated text from the response
        if (result.get('candidates') and 
            result['candidates'][0].get('content') and 
            result['candidates'][0]['content'].get('parts')):
            
            llm_response = result['candidates'][0]['content']['parts'][0]['text']
            logging.info("LLM synthesis successful.")
            return llm_response
        else:
            logging.error(f"Unexpected LLM response format: {result}")
            return "Sorry, I received an unusual response from my AI brain. Please try again."

    except requests.exceptions.RequestException as e:
        logging.error(f"LLM API request failed: {e}")
        return "Sorry, I'm having trouble connecting to my AI brain right now. Please check the connection."
    except Exception as e:
        logging.error(f"An unexpected error occurred during LLM synthesis: {e}")
        return "An unexpected error occurred while generating the response."
