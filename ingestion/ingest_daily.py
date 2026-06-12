import os
import json
import logging
from datetime import datetime
from ingestion.scraper import fetch_url
from ingestion.parser import parse_next_data, parse_faqs, extract_structured_data, build_markdown_document
from ingestion.indexing import build_index

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ingest_daily")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_PATH = os.path.join(BASE_DIR, "config", "corpus_registry.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")

def validate_record(record: dict) -> bool:
    """
    Validates the parsed mutual fund record.
    Returns True if valid, False otherwise.
    """
    # 1. Check scheme_name
    if not record.get("scheme_name"):
        logger.error(f"Validation Error: scheme_name is missing or empty for {record.get('scheme_id')}.")
        return False
        
    # 2. Check NAV
    nav = record.get("nav")
    if nav is None:
        logger.error(f"Validation Error: NAV is missing for {record.get('scheme_name')}.")
        return False
    try:
        if float(nav) <= 0:
            logger.error(f"Validation Error: NAV must be greater than 0. Found: {nav} for {record.get('scheme_name')}.")
            return False
    except ValueError:
        logger.error(f"Validation Error: NAV is not a valid number. Found: {nav} for {record.get('scheme_name')}.")
        return False
        
    # 3. Check Exit Load
    exit_load = record.get("exit_load")
    if not exit_load or not isinstance(exit_load, str) or not exit_load.strip():
        logger.error(f"Validation Error: Exit Load is missing or empty for {record.get('scheme_name')}.")
        return False
        
    # 4. Check AUM
    aum = record.get("aum")
    if aum is None:
        logger.error(f"Validation Error: AUM is missing for {record.get('scheme_name')}.")
        return False
        
    return True

def run_ingestion():
    logger.info("Starting Mutual Fund FAQ Assistant Daily Ingestion Task...")
    
    # Check if corpus registry exists
    if not os.path.exists(REGISTRY_PATH):
        logger.error(f"Corpus registry not found at {REGISTRY_PATH}")
        return
        
    # Load corpus registry
    try:
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load corpus registry: {e}")
        return
        
    schemes = registry.get("schemes", [])
    if not schemes:
        logger.warning("No mutual fund schemes found in the corpus registry.")
        return
        
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logger.info(f"Target processed data directory: {OUTPUT_DIR}")
    
    today_str = datetime.today().strftime("%Y-%m-%d")
    success_count = 0
    failure_count = 0
    
    for scheme in schemes:
        scheme_id = scheme.get("id")
        url = scheme.get("url")
        expected_name = scheme.get("scheme_name")
        
        logger.info(f"Processing scheme: {expected_name} ({scheme_id}) from {url}")
        
        try:
            # 1. Scrape HTML page
            html_content = fetch_url(url)
            
            # 2. Parse Next.js structured state
            mf_data = parse_next_data(html_content)
            
            # 3. Parse JSON-LD FAQs
            faqs = parse_faqs(html_content)
            
            # 4. Map structured records
            record = extract_structured_data(mf_data, faqs, scheme_id, url, today_str)
            
            # 5. Validate the record
            if not validate_record(record):
                logger.error(f"Validation failed for scheme {scheme_id}. Skipping storage.")
                failure_count += 1
                continue
                
            # 6. Build the plain text markdown document representation
            markdown_content = build_markdown_document(record)
            
            # 7. Write outputs to files
            json_file_path = os.path.join(OUTPUT_DIR, f"{scheme_id}.json")
            txt_file_path = os.path.join(OUTPUT_DIR, f"{scheme_id}.txt")
            
            with open(json_file_path, "w", encoding="utf-8") as jf:
                json.dump(record, jf, indent=2, ensure_ascii=False)
                
            with open(txt_file_path, "w", encoding="utf-8") as tf:
                tf.write(markdown_content)
                
            logger.info(f"Successfully saved structured and text documents for {scheme_id}.")
            success_count += 1
            
        except Exception as e:
            logger.exception(f"Unhandled exception during ingestion of {scheme_id}: {e}")
            failure_count += 1
            
    logger.info(f"Ingestion completed. Success: {success_count}, Failures: {failure_count}")
    if success_count > 0:
        logger.info("New data ingested. Rebuilding vector index...")
        try:
            build_index()
            logger.info("Vector index rebuilt successfully.")
        except Exception as e:
            logger.error(f"Failed to rebuild vector index: {e}")

if __name__ == "__main__":
    run_ingestion()
