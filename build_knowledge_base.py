# build_knowledge_base.py
# This script takes the scraped data and builds our AI knowledge base,
# consisting of a FAISS index and the corresponding text chunks.

import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import logging
import os

# --- Configuration ---
INPUT_DATA_FILE = "scraped_data.json"
INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.pkl"

def build_and_save_knowledge_base():
    """
    Loads scraped data, creates embeddings, builds a FAISS index,
    and saves the index and text chunks to files.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 1. Load the scraped data
    if not os.path.exists(INPUT_DATA_FILE):
        logging.error(f"Input file '{INPUT_DATA_FILE}' not found. Please run scraper.py first.")
        return
        
    with open(INPUT_DATA_FILE, 'r', encoding='utf-8') as f:
        text_chunks = json.load(f)

    if not text_chunks:
        logging.error("Scraped data file is empty. Nothing to build.")
        return
        
    logging.info(f"Loaded {len(text_chunks)} text chunks from '{INPUT_DATA_FILE}'.")

    # 2. Create vector embeddings
    logging.info("Loading sentence transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    logging.info("Creating vector embeddings for text chunks. This may take a moment...")
    embeddings = model.encode(text_chunks, show_progress_bar=True)
    logging.info(f"Embeddings created with shape: {embeddings.shape}")

    # 3. Build the FAISS index
    logging.info("Building FAISS index...")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings, dtype=np.float32))
    logging.info(f"FAISS index built successfully. Total entries: {index.ntotal}")

    # 4. Save the index and the text chunks
    logging.info(f"Saving FAISS index to '{INDEX_FILE}'...")
    faiss.write_index(index, INDEX_FILE)
    
    logging.info(f"Saving text chunks to '{CHUNKS_FILE}'...")
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(text_chunks, f)
    
    logging.info("Knowledge base build process complete!")


if __name__ == "__main__":
    build_and_save_knowledge_base()
