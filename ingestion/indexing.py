import os
import json
import re
from typing import List, Dict, Any
from retrieval.vector_store import VectorStore

def clean_section_name(name: str) -> str:
    """Clean markdown headings to be used as labels."""
    return re.sub(r'[#\s\-\:\?]', '_', name.strip().lower()).strip('_')

def parse_markdown_sections(file_path: str, scheme_name: str) -> List[Dict[str, Any]]:
    """
    Parses the normalized mutual fund text file into logical chunks.
    Preserves tables intact, groups FAQs by Q&A pairs, and handles manager profiles.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split("\n")
    chunks = []
    
    current_h2 = ""
    current_h3 = ""
    current_text_lines = []
    
    def flush_chunk():
        nonlocal current_text_lines, current_h2, current_h3
        text_block = "\n".join(current_text_lines).strip()
        if not text_block:
            return
            
        section_path = f"{scheme_name} > {current_h2}"
        if current_h3:
            section_path += f" > {current_h3}"
            
        full_chunk_text = f"{section_path}\n{text_block}"
        
        # Determine section type for metadata
        sec_type = "general"
        h2_clean = clean_section_name(current_h2)
        if "metric" in h2_clean:
            sec_type = "metrics"
        elif "objective" in h2_clean:
            sec_type = "objective"
        elif "holding" in h2_clean:
            sec_type = "holdings"
        elif "manager" in h2_clean:
            sec_type = "fund_managers"
        elif "faq" in h2_clean or "question" in h2_clean:
            sec_type = "faqs"
        elif "info" in h2_clean:
            sec_type = "scheme_information"
            
        # Refined chunking for holdings to avoid embedding truncation and dilution
        if sec_type == "holdings":
            lines = text_block.split("\n")
            table_lines = [line.strip() for line in lines if line.strip().startswith("|")]
            if len(table_lines) >= 3:
                header = table_lines[0]
                separator = table_lines[1]
                data_rows = table_lines[2:]
                
                # 1. Top 10 Holdings Table
                top_10_data = data_rows[:10]
                top_10_table = "\n".join([header, separator] + top_10_data)
                chunks.append({
                    "text": f"{section_path} (Top 10)\n{top_10_table}",
                    "section_type": sec_type,
                    "section_path": f"{section_path} > Top 10"
                })
                
                # 2. Individual Holding Chunks
                for row in data_rows:
                    cols = [c.strip() for c in row.split("|")]
                    if len(cols) >= 7 and cols[1] and not cols[1].startswith("---") and not cols[1].startswith(":---"):
                        company = cols[1]
                        sector = cols[2]
                        nature = cols[3]
                        instrument = cols[4]
                        rating = cols[5]
                        allocation = cols[6]
                        
                        stmt = f"{scheme_name} holds {allocation} of its corpus in {company} (Sector: {sector}, Nature: {nature}, Instrument: {instrument}, Rating: {rating})."
                        chunks.append({
                            "text": f"{section_path} > {company}\n{stmt}",
                            "section_type": sec_type,
                            "section_path": f"{section_path} > {company}"
                        })
            else:
                chunks.append({
                    "text": full_chunk_text,
                    "section_type": sec_type,
                    "section_path": section_path
                })
        # Recursive split if chunk exceeds size limits (e.g. manager profiles with long lists)
        # Avoid splitting tables or structured metric blocks if possible
        elif len(text_block) > 1200 and sec_type not in ["metrics"]:
            sub_chunks = recursive_split(text_block, chunk_size=1000, overlap=200)
            for i, sub_txt in enumerate(sub_chunks):
                chunks.append({
                    "text": f"{section_path} (Part {i+1})\n{sub_txt}",
                    "section_type": sec_type,
                    "section_path": section_path
                })
        else:
            chunks.append({
                "text": full_chunk_text,
                "section_type": sec_type,
                "section_path": section_path
            })
            
        current_text_lines = []

    def recursive_split(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple recursive splitter by lines or spaces to avoid mid-word truncation."""
        paragraphs = text.split("\n\n")
        sub_chunks = []
        current_chunk = []
        current_len = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if current_len + len(para) <= chunk_size:
                current_chunk.append(para)
                current_len += len(para) + 2
            else:
                if current_chunk:
                    sub_chunks.append("\n\n".join(current_chunk))
                # Set up next chunk with overlap
                current_chunk = [para]
                current_len = len(para)
                
        if current_chunk:
            sub_chunks.append("\n\n".join(current_chunk))
            
        # Fallback to character splitting if a single paragraph is too large
        final_chunks = []
        for chunk in sub_chunks:
            if len(chunk) > chunk_size + 200:
                # Character split with overlap
                start = 0
                while start < len(chunk):
                    end = start + chunk_size
                    final_chunks.append(chunk[start:end])
                    if end >= len(chunk):
                        break
                    start = end - overlap
            else:
                final_chunks.append(chunk)
                
        return final_chunks

    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check H2 heading
        if line.startswith("## "):
            flush_chunk()
            current_h2 = line[3:].strip()
            current_h3 = ""
            
        # Check H3 heading
        elif line.startswith("### "):
            flush_chunk()
            current_h3 = line[4:].strip()
            
        # Ignore H1 title lines since they are global
        elif line.startswith("# "):
            pass
            
        else:
            current_text_lines.append(line)
            
        i += 1
        
    flush_chunk()  # Flush final chunk
    return chunks

def build_index():
    print("Initializing Ingestion & Indexing Pipeline...")
    
    # Load registry
    registry_path = "config/corpus_registry.json"
    if not os.path.exists(registry_path):
        raise FileNotFoundError(f"Registry config not found at {registry_path}")
        
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
        
    processed_dir = "data/processed"
    if not os.path.exists(processed_dir):
        raise FileNotFoundError(f"Processed directory not found at {processed_dir}")
        
    # Initialize local VectorStore
    # We use BGE small for fast local CPU computation by default
    vector_store = VectorStore(embedding_model_name="BAAI/bge-small-en-v1.5")
    
    all_texts = []
    all_metadatas = []
    
    for scheme in registry["schemes"]:
        scheme_id = scheme["id"]
        scheme_name = scheme["scheme_name"]
        
        txt_file = os.path.join(processed_dir, f"{scheme_id}.txt")
        json_file = os.path.join(processed_dir, f"{scheme_id}.json")
        
        if not os.path.exists(txt_file) or not os.path.exists(json_file):
            print(f"Skipping {scheme_name} ({scheme_id}): Cleaned data files not found.")
            continue
            
        print(f"Processing index chunks for: {scheme_name}...")
        
        # Read JSON metadata parameters
        with open(json_file, "r", encoding="utf-8") as jf:
            scheme_data = json.load(jf)
            
        scrape_date = scheme_data.get("scrape_date", "2026-06-10")
        category = scheme_data.get("category", "Equity")
        risk_level = scheme_data.get("risk_level", "Very High")
        source_url = scheme_data.get("url", scheme["url"])
        
        # Chunk text file content
        parsed_chunks = parse_markdown_sections(txt_file, scheme_name)
        
        for chunk in parsed_chunks:
            # Enriched metadata schema as per Phase 2.2
            meta = {
                "scheme_id": scheme_id,
                "scheme_name": scheme_name,
                "source_url": source_url,
                "last_updated_date": scrape_date,
                "category": category,
                "risk_level": risk_level,
                "section_type": chunk["section_type"],
                "section_path": chunk["section_path"]
            }
            all_texts.append(chunk["text"])
            all_metadatas.append(meta)
            
    if not all_texts:
        print("Error: No documents were parsed to index.")
        return
        
    print(f"Total parsed chunks to index: {len(all_texts)}")
    print("Generating embeddings and writing to local FAISS store...")
    
    vector_store.add_documents(all_texts, all_metadatas)
    vector_store.save()
    print("Vector Store successfully indexed and saved!")

if __name__ == "__main__":
    build_index()
