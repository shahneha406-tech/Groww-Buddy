import sys
import os

# Add root folder to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

from retrieval.vector_store import VectorStore

def test_search():
    print("Loading VectorStore...")
    # Initialize vector store
    store = VectorStore()
    
    # Test queries
    queries = [
        ("What is the exit load of HDFC Small Cap Fund?", "hdfc_small_cap"),
        ("Who is the fund manager of HDFC Defence Fund?", "hdfc_defence"),
        ("What is the expense ratio of HDFC Top 100 Fund?", "hdfc_large_cap")
    ]
    
    for query, scheme_id in queries:
        print("\n" + "="*80)
        print(f"QUERY: {query}")
        print(f"FILTER SCHEME: {scheme_id}")
        print("="*80)
        
        results = store.similarity_search(query, k=3, filter_scheme_id=scheme_id)
        print(f"Found {len(results)} results:")
        for idx, res in enumerate(results):
            print(f"\n--- Match {idx+1} (Score: {res['score']:.4f}) ---")
            print(f"Path: {res['metadata'].get('section_path')}")
            print(f"Text Snippet:\n{res['text'][:300]}")
            print("-" * 40)

if __name__ == "__main__":
    test_search()
