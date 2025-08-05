# scraper.py
# This is the best possible "Librarian" script. It uses advanced techniques
# to intelligently extract text, clean it, and process tables to build a
# high-fidelity knowledge base from websites and any kind of PDF.

import requests
from bs4 import BeautifulSoup
import json
import logging
import os
import pdfplumber
import re

# --- Configuration ---
URLS_TO_SCRAPE = [
    "https://agriwelfare.gov.in/en/Major"
]
PDF_FOLDER = "policy_advisor_pdfs"
OUTPUT_FILE = "scraped_data.json"

def scrape_websites():
    """Scrapes the configured URLs and returns a list of text chunks."""
    logging.info("--- Starting Website Scraping Phase ---")
    web_chunks = []
    for url in URLS_TO_SCRAPE:
        try:
            logging.info(f"Scraping data from: {url}")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            rows = soup.select("div.table-responsive table tbody tr")
            
            for row in rows:
                cols = row.find_all('td')
                if len(cols) > 1:
                    scheme_name = cols[1].text.strip()
                    link_tag = cols[3].find('a')
                    scheme_link = requests.compat.urljoin(url, link_tag['href']) if link_tag and link_tag.get('href') else "No link available"
                    chunk = f"Information about the scheme named '{scheme_name}'. More details can be found at the official link: {scheme_link}"
                    web_chunks.append(chunk)
            logging.info(f"Found {len(web_chunks)} schemes on {url}")
        except Exception as e:
            logging.error(f"Failed to scrape URL {url}. Error: {e}")
    return web_chunks

def clean_text(text):
    """A helper function to clean common text issues from PDFs."""
    # Remove excessive newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remove page numbers that are often at the start/end of a line
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    return text.strip()

def scrape_local_pdfs():
    """
    Scrapes all PDF files from the local PDF_FOLDER, intelligently extracting
    and cleaning plain text and structured tables page by page.
    """
    logging.info("--- Starting Local PDF Scraping Phase ---")
    pdf_chunks = []
    if not os.path.exists(PDF_FOLDER):
        logging.warning(f"PDF folder '{PDF_FOLDER}' not found. Skipping PDF scraping.")
        return pdf_chunks

    for filename in os.listdir(PDF_FOLDER):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(PDF_FOLDER, filename)
            try:
                logging.info(f"Reading PDF: {filename}")
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        page_content = ""
                        
                        # 1. Extract and clean plain text from the page
                        raw_text = page.extract_text()
                        if raw_text:
                            page_content += clean_text(raw_text) + "\n\n"

                        # 2. Extract, clean, and format tables from the page
                        tables = page.extract_tables()
                        if tables:
                            logging.info(f"Found {len(tables)} table(s) on page {i+1} of {filename}")
                            for table in tables:
                                # Clean the table data from None values and extra whitespace
                                cleaned_table = [[str(cell).strip() if cell is not None else "" for cell in row] for row in table]
                                # Convert table data into a clean, readable Markdown format
                                table_text = "\n".join(["| " + " | ".join(row) + " |" for row in cleaned_table])
                                page_content += "The following is a table with important data:\n" + table_text + "\n\n"
                        
                        # 3. Create a final, clean chunk for this page
                        if page_content.strip():
                            # Each page becomes a separate chunk with its source for context
                            final_chunk = f"Information from document '{filename}' (Page {i+1}):\n{page_content.strip()}"
                            pdf_chunks.append(final_chunk)
                
                logging.info(f"Successfully processed {len(pdf.pages)} pages from {filename}.")
            except Exception as e:
                logging.error(f"Failed to read PDF {filename}. Error: {e}")
    return pdf_chunks


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    web_data = scrape_websites()
    pdf_data = scrape_local_pdfs()
    
    all_data = web_data + pdf_data
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
        
    logging.info(f"Scraping complete. Created a total of {len(all_data)} knowledge chunks.")
    logging.info(f"All data saved to '{OUTPUT_FILE}'")
