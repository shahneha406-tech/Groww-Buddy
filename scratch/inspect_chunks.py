import sys
import os
import pickle
from collections import Counter

# Add root folder to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

def analyze():
    metadata_file = "data/vector_store/metadata.pkl"
    if not os.path.exists(metadata_file):
        print("Metadata file not found! Run indexing first.")
        return
        
    with open(metadata_file, "rb") as f:
        documents = pickle.load(f)
        
    print(f"Total Chunks in Vector Store: {len(documents)}")
    print("=" * 60)
    
    # Analyze by scheme_id
    schemes = [doc["metadata"]["scheme_id"] for doc in documents.values()]
    print("Chunks per Scheme:")
    for scheme, count in Counter(schemes).items():
        print(f"  - {scheme}: {count}")
    print("=" * 60)
    
    # Analyze by section_type
    sections = [doc["metadata"]["section_type"] for doc in documents.values()]
    print("Chunks per Section Type:")
    for sec, count in Counter(sections).items():
        print(f"  - {sec}: {count}")
    print("=" * 60)
    
    # Analyze chunk lengths
    lengths = [len(doc["text"]) for doc in documents.values()]
    print("Chunk Character Length Statistics:")
    print(f"  - Min: {min(lengths)} characters")
    print(f"  - Max: {max(lengths)} characters")
    print(f"  - Avg: {sum(lengths)/len(lengths):.1f} characters")
    print("=" * 60)
    
    # Show samples of each section type to understand structural differences
    seen_types = set()
    print("Sample Chunk Structure by Section Type:")
    for doc in documents.values():
        sec_type = doc["metadata"]["section_type"]
        if sec_type not in seen_types:
            seen_types.add(sec_type)
            print(f"\n--- Section Type: {sec_type} ---")
            print(f"Path: {doc['metadata'].get('section_path')}")
            print("Content (First 150 chars):")
            print(doc["text"][:150] + "...")
            print("-" * 40)

if __name__ == "__main__":
    analyze()
