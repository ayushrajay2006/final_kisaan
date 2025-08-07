# update_knowledge_base.py
# This is the final, intelligent script for managing your AI's knowledge base.
# It finds and processes ONLY new PDF files and new URLs, adding them to the
# existing knowledge base without re-scraping old content.

import json
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import logging
import os
import pdfplumber
import re
import requests
from bs4 import BeautifulSoup

# --- Configuration ---
PDF_FOLDER = "knowledge_base_pdfs"
URL_SOURCE_FILE = "sources.txt" # The file for your URLs
INDEX_FILE = "index.faiss"
CHUNKS_FILE = "chunks.pkl"
# This file tracks both PDFs and URLs that have already been processed
TRACKING_FILE = "processed_sources.json"

def clean_text(text):
    """A helper function to clean common text issues."""
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    return text.strip()

def get_processed_sources():
    """Loads the set of already processed filenames and URLs."""
    if not os.path.exists(TRACKING_FILE):
        return set()
    with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
        return set(json.load(f))

def save_processed_sources(processed_sources):
    """Saves the updated set of processed filenames and URLs."""
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_sources), f)

def scrape_new_pdfs(processed_sources):
    """Scrapes ONLY the new PDF files."""
    logging.info("--- Checking for new PDF files ---")
    new_pdf_chunks = []
    newly_processed_files = []
    if not os.path.exists(PDF_FOLDER):
        return [], []
    for filename in os.listdir(PDF_FOLDER):
        if filename.lower().endswith(".pdf") and filename not in processed_sources:
            logging.info(f"New file found: {filename}. Processing...")
            file_path = os.path.join(PDF_FOLDER, filename)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        page_content = ""
                        raw_text = page.extract_text()
                        if raw_text: page_content += clean_text(raw_text) + "\n\n"
                        tables = page.extract_tables()
                        if tables:
                            for table in tables:
                                cleaned_table = [[str(cell).strip() if cell is not None else "" for cell in row] for row in table]
                                table_text = "\n".join(["| " + " | ".join(row) + " |" for row in cleaned_table])
                                page_content += "The following is a table with important data:\n" + table_text + "\n\n"
                        if page_content.strip():
                            final_chunk = f"Information from document '{filename}' (Page {i+1}):\n{page_content.strip()}"
                            new_pdf_chunks.append(final_chunk)
                newly_processed_files.append(filename)
                logging.info(f"Successfully processed {len(pdf.pages)} pages from new file {filename}.")
            except Exception as e:
                logging.error(f"Failed to read new PDF {filename}. Error: {e}")
    return new_pdf_chunks, newly_processed_files

def scrape_new_urls(processed_sources):
    """Scrapes ONLY the new URLs from the source file."""
    logging.info("--- Checking for new URLs ---")
    new_url_chunks = []
    newly_processed_urls = []
    if not os.path.exists(URL_SOURCE_FILE):
        logging.warning(f"URL source file '{URL_SOURCE_FILE}' not found. Skipping web scraping.")
        return [], []
    
    with open(URL_SOURCE_FILE, 'r', encoding='utf-8') as f:
        urls_to_scrape = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for url in urls_to_scrape:
        if url not in processed_sources:
            logging.info(f"New URL found: {url}. Scraping...")
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                cleaned_chunk = clean_text(text)
                final_chunk = f"Information from website '{url}':\n{cleaned_chunk}"
                new_url_chunks.append(final_chunk)
                newly_processed_urls.append(url)
                logging.info(f"Successfully scraped and processed new URL: {url}")
            except Exception as e:
                logging.error(f"Failed to scrape new URL {url}. Error: {e}")

    return new_url_chunks, newly_processed_urls

def update_knowledge_base():
    """
    The main function to incrementally update the knowledge base from both PDFs and URLs.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Smart Transition Logic: If the knowledge base exists but the tracking file doesn't,
    # create the tracking file to prevent re-scraping everything you've already done.
    if os.path.exists(INDEX_FILE) and not os.path.exists(TRACKING_FILE):
        logging.warning("Existing knowledge base found, but no tracking file. Creating a baseline tracking file.")
        initial_sources = set()
        if os.path.exists(PDF_FOLDER):
            initial_sources.update([f for f in os.listdir(PDF_FOLDER) if f.lower().endswith('.pdf')])
        if os.path.exists(URL_SOURCE_FILE):
            with open(URL_SOURCE_FILE, 'r', encoding='utf-8') as f:
                initial_sources.update([line.strip() for line in f if line.strip() and not line.startswith('#')])
        save_processed_sources(initial_sources)
        logging.info("Baseline tracking file created. Run the update again to process any new content added after the baseline.")
        return

    processed_sources = get_processed_sources()
    
    new_pdf_chunks, newly_processed_pdfs = scrape_new_pdfs(processed_sources)
    new_url_chunks, newly_processed_urls = scrape_new_urls(processed_sources)
    
    new_chunks = new_pdf_chunks + new_url_chunks
    
    if not new_chunks:
        logging.info("No new content found. Knowledge base is already up-to-date.")
        return

    logging.info(f"Found {len(new_chunks)} new text chunks to add to the knowledge base.")

    if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):
        logging.info("Loading existing knowledge base...")
        index = faiss.read_index(INDEX_FILE)
        with open(CHUNKS_FILE, "rb") as f:
            all_chunks = pickle.load(f)
    else:
        logging.info("No existing knowledge base found. Creating a new one.")
        index = None
        all_chunks = []

    logging.info("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logging.info("Creating embeddings for new chunks...")
    new_embeddings = model.encode(new_chunks, show_progress_bar=True)

    if index is None:
        index = faiss.IndexFlatL2(new_embeddings.shape[1])
    
    index.add(np.array(new_embeddings, dtype=np.float32))
    all_chunks.extend(new_chunks)

    logging.info(f"Saving updated FAISS index to '{INDEX_FILE}'...")
    faiss.write_index(index, INDEX_FILE)
    
    logging.info(f"Saving updated text chunks to '{CHUNKS_FILE}'...")
    with open(CHUNKS_FILE, "wb") as f:
        pickle.dump(all_chunks, f)

    processed_sources.update(newly_processed_pdfs)
    processed_sources.update(newly_processed_urls)
    save_processed_sources(processed_sources)

    logging.info("Knowledge base update complete!")
    logging.info(f"Total chunks in knowledge base: {len(all_chunks)}")


if __name__ == "__main__":
    update_knowledge_base()
