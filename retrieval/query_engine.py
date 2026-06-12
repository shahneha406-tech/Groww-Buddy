import os
from retrieval.retriever import MutualFundRetriever
from retrieval.llm_client import GroqClient
from validation.validator import ResponseValidator
from formatter.formatter import ResponseFormatter
from validation.guardrails import GuardrailsManager

class MutualFundQueryEngine:
    def __init__(self, index_dir: str = "./data/vector_store", embedding_model_name: str = "BAAI/bge-small-en-v1.5"):
        self.retriever = MutualFundRetriever(index_dir=index_dir, embedding_model_name=embedding_model_name)
        self.llm_client = GroqClient()
        self.validator = ResponseValidator()
        self.formatter = ResponseFormatter()
        self.guardrails = GuardrailsManager()

    def query(self, query_str: str) -> str:
        """
        Processes a user query through the complete RAG pipeline.
        Returns the validated, formatted response.
        """
        # 1. Pre-retrieval Guardrails: PII Check
        if self.guardrails.detect_pii(query_str):
            return "I cannot process queries containing personal identifier information (PII) like PAN, Aadhaar, email, or bank accounts for security reasons. Please try again without sharing personal details."

        # 2. Pre-retrieval Guardrails: Intent Check
        intent = self.guardrails.classify_intent(query_str)
        if intent == "greetings":
            return "Hello! I am Groww Buddy, your factual HDFC Mutual Fund FAQ assistant. How can I help you today? You can ask me about fund details, such as exit loads, expense ratios, holdings, and managers."
            
        if intent == "advisory":
            return "I am a factual FAQ assistant and cannot provide investment recommendations, advisory opinions, or fund comparisons. Please refer to the official investor education resources below."

        if intent == "out-of-scope":
            return "I am a specialized assistant for HDFC Mutual Funds and can only answer questions related to mutual funds. Your query appears to be outside this domain."

        # 3. Retrieval
        retrieved_chunks = self.retriever.retrieve(query_str, k=3)
        if not retrieved_chunks:
            # Reconstruct fallback citation/date if possible from a default or return general fallback
            return self.formatter.format("I cannot find this information in the official documents.", [])

        # 2. LLM Answer Generation
        raw_answer = self.llm_client.generate_answer(query_str, retrieved_chunks)

        # 3. Post-Generation Validation
        is_valid, validated_answer = self.validator.validate(raw_answer, retrieved_chunks)

        # 4. Response Formatting
        # Note: Even if it's invalid, the validator returns a standard fallback string (e.g. "I cannot find this...")
        # which we still want to format with citation/footer if chunks were retrieved.
        final_response = self.formatter.format(validated_answer, retrieved_chunks)
        return final_response

if __name__ == "__main__":
    # Quick execution test
    # Set mock key if not set to run without error in dry run
    if not os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEY"] = "mock_key_for_testing"
        
    engine = MutualFundQueryEngine()
    q = "What is the exit load of HDFC Small Cap Fund?"
    print(f"Query: {q}")
    response = engine.query(q)
    print("\nResponse:")
    print(response)
