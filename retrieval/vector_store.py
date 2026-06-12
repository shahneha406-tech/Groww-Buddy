import os
import json
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class VectorStore:
    def __init__(self, index_dir: str = "./data/vector_store", embedding_model_name: str = "BAAI/bge-small-en-v1.5"):
        self.index_dir = index_dir
        self.embedding_model_name = embedding_model_name
        self.index_file = os.path.join(index_dir, "index.faiss")
        self.metadata_file = os.path.join(index_dir, "metadata.pkl")
        
        self.index = None
        self.documents: Dict[int, Dict[str, Any]] = {}
        self.embeddings_model = None
        self.dimension = None
        
        # Ensure directory exists
        os.makedirs(self.index_dir, exist_ok=True)
        
    def _get_embedding_model(self):
        """Lazy load the embedding model to avoid unnecessary overhead."""
        if self.embeddings_model is not None:
            return self.embeddings_model
            
        # Check if we explicitly want Gemini embeddings
        if self.embedding_model_name == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required to use Gemini embeddings.")
            print("Using Gemini API for Embeddings...")
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.embeddings_model = "gemini"
            self.dimension = 768  # text-embedding-004 output dimension
        else:
            print(f"Loading local SentenceTransformer model: {self.embedding_model_name}...")
            from sentence_transformers import SentenceTransformer
            self.embeddings_model = SentenceTransformer(self.embedding_model_name)
            if hasattr(self.embeddings_model, "get_embedding_dimension"):
                self.dimension = self.embeddings_model.get_embedding_dimension()
            else:
                self.dimension = self.embeddings_model.get_sentence_embedding_dimension()
            
        return self.embeddings_model

    def _embed_text(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts."""
        model = self._get_embedding_model()
        if model == "gemini":
            import google.generativeai as genai
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result["embedding"])
            return np.array(embeddings, dtype=np.float32)
        else:
            # SentenceTransformer returns numpy array
            embeddings = model.encode(texts, normalize_embeddings=True)
            return np.array(embeddings, dtype=np.float32)

    def _embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for a single query."""
        model = self._get_embedding_model()
        if model == "gemini":
            import google.generativeai as genai
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            embedding = result["embedding"]
            return np.array(embedding, dtype=np.float32).reshape(1, -1)
        else:
            # SentenceTransformer encode
            embedding = model.encode(query, normalize_embeddings=True)
            return np.array(embedding, dtype=np.float32).reshape(1, -1)

    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """Embed and add documents to the FAISS index and local mapping."""
        if not texts:
            return
            
        assert len(texts) == len(metadatas), "Texts and metadatas lists must be of equal length"
        
        # Generate embeddings
        embeddings = self._embed_text(texts)
        
        # Initialize FAISS index if it doesn't exist
        if self.index is None:
            self.dimension = embeddings.shape[1]
            # L2 distance index for normalized vectors is equivalent to cosine similarity
            self.index = faiss.IndexFlatIP(self.dimension)
            
        # Get start vector ID
        start_id = len(self.documents)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Save documents and metadata
        for i, (text, meta) in enumerate(zip(texts, metadatas)):
            doc_id = start_id + i
            self.documents[doc_id] = {
                "text": text,
                "metadata": meta
            }
            
    def save(self):
        """Persist index and metadata to disk."""
        if self.index is None:
            print("Index is empty, nothing to save.")
            return
            
        # Save FAISS index
        faiss.write_index(self.index, self.index_file)
        
        # Save metadata mapping
        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.documents, f)
            
        print(f"Successfully saved vector store with {len(self.documents)} documents to {self.index_dir}")

    def load(self):
        """Load index and metadata from disk."""
        if not os.path.exists(self.index_file) or not os.path.exists(self.metadata_file):
            raise FileNotFoundError(f"Vector store files not found in {self.index_dir}. Please run indexing first.")
            
        # Load FAISS index
        self.index = faiss.read_index(self.index_file)
        self.dimension = self.index.d
        
        # Load metadata mapping
        with open(self.metadata_file, "rb") as f:
            self.documents = pickle.load(f)
            
        print(f"Successfully loaded vector store with {len(self.documents)} documents from {self.index_dir}")

    def similarity_search(self, query: str, k: int = 4, filter_scheme_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the vector store for similar documents with optional scheme_id filtering."""
        if self.index is None:
            self.load()
            
        # Generate query embedding
        query_vector = self._embed_query(query)
        
        # If filtering is active, we can retrieve more candidates first to ensure we get k matches after filtering
        search_k = k * 5 if filter_scheme_id else k
        search_k = min(search_k, len(self.documents))
        
        if search_k == 0:
            return []
            
        # Search FAISS index
        distances, indices = self.index.search(query_vector, search_k)
        
        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
                
            doc = self.documents.get(int(idx))
            if doc:
                # Scheme filtering in Python
                meta = doc["metadata"]
                if filter_scheme_id and meta.get("scheme_id") != filter_scheme_id:
                    continue
                    
                results.append({
                    "text": doc["text"],
                    "metadata": meta,
                    "score": float(score)
                })
                
                if len(results) == k:
                    break
                    
        return results
