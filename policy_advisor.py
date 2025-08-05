# policy_advisor.py
# CONVERSATIONAL VERSION: This agent now acts as a pure "tool". Its only job is to
# search the knowledge base and return the most relevant documents.

import logging
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os

# --- Configuration ---
INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.pkl"

# --- Load the Knowledge Base into Memory on Startup ---
knowledge_base = None
model = None
try:
    if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):
        logging.info("Loading pre-built knowledge base...")
        index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "rb") as f:
            chunks = pickle.load(f)
        knowledge_base = {"index": index, "chunks": chunks}
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logging.info("Knowledge base loaded successfully.")
    else:
        logging.error("Knowledge base files not found!")
except Exception as e:
    logging.error(f"Failed to load knowledge base on startup. Error: {e}")


def get_scheme_information(question: str, chat_history: list):
    """
    Acts as a tool to retrieve relevant scheme information from the knowledge base.
    """
    if not knowledge_base or not model:
        return None # Return None if the KB isn't loaded

    try:
        # For follow-up questions, the context is in the history. For new questions, it's in the question itself.
        # A more advanced implementation could summarize the history, but for now, we'll focus on the latest question.
        search_query = question
        
        logging.info(f"Searching knowledge base for: '{search_query}'")
        question_embedding = model.encode([search_query])
        
        # Search the index for the 3 most similar chunks
        D, I = index.search(np.array(question_embedding, dtype=np.float32), k=3)
        
        retrieved_chunks = [knowledge_base["chunks"][i] for i in I[0]]
        context = "\n\n---\n\n".join(retrieved_chunks)
        
        logging.info("Retrieved relevant context from knowledge base.")
        
        # Return the raw context. The LLM processor will handle the generation.
        return {
            "retrieved_information_from_government_sources": context
        }

    except Exception as e:
        logging.error(f"Error during RAG retrieval: {e}")
        return None
