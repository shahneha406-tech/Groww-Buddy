import re
from typing import List, Dict, Any, Optional
from retrieval.vector_store import VectorStore

class MutualFundRetriever:
    def __init__(self, index_dir: str = "./data/vector_store", embedding_model_name: str = "BAAI/bge-small-en-v1.5"):
        self.vector_store = VectorStore(index_dir=index_dir, embedding_model_name=embedding_model_name)
        
    def detect_scheme(self, query: str) -> Optional[str]:
        """
        Detects the mutual fund scheme mentioned in the query.
        Returns the scheme_id if detected, else None.
        """
        query_lower = query.lower()
        
        # Mapping patterns to scheme IDs
        # Priority checks to avoid false positives (e.g. 'mid cap' before 'large cap' if query has both)
        mappings = {
            "hdfc_defence": [r"\bdefence\b", r"\bdefense\b"],
            "hdfc_small_cap": [r"\bsmall\s*cap\b", r"\bsmallcap\b"],
            "hdfc_mid_cap": [r"\bmid\s*cap\b", r"\bmidcap\b", r"\bopportunities\b"],
            "hdfc_large_cap": [r"\blarge\s*cap\b", r"\blargecap\b", r"\btop\s*100\b"],
            "hdfc_gold_foh": [r"\bgold\b", r"\bgold\s*etf\b", r"\bgold\s*fof\b"]
        }
        
        for scheme_id, patterns in mappings.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return scheme_id
                    
        return None

    def retrieve(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top k relevant documents with automatic scheme metadata filtering.
        """
        scheme_id = self.detect_scheme(query)
        # Search FAISS index
        return self.vector_store.similarity_search(query, k=k, filter_scheme_id=scheme_id)

if __name__ == "__main__":
    # Quick sanity check
    retriever = MutualFundRetriever()
    q = "What is the exit load of HDFC Small Cap Fund?"
    results = retriever.retrieve(q, k=3)
    print(f"Query: {q}")
    print(f"Detected Scheme: {retriever.detect_scheme(q)}")
    print(f"Retrieved {len(results)} chunks:")
    for r in results:
        print(f"  - {r['metadata']['section_path']} (score: {r['score']:.4f})")
