import os
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    def __init__(self, model_name: str = None):
        self.api_key = os.environ.get("GROQ_API_KEY")
        # Default model is llama-3.1-8b-instant, which is fast and accurate for RAG
        self.model_name = model_name or os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        if not self.api_key:
            print("Warning: GROQ_API_KEY environment variable not found. LLM calls will fail.")

    def generate_answer(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Generates a concise facts-only answer based on retrieved context chunks.
        """
        if not self.api_key:
            return "Error: Groq API key is missing. Cannot generate answer."
            
        # Reconstruct context block
        context_str = ""
        for idx, chunk in enumerate(retrieved_chunks):
            context_str += f"Context {idx+1} (Source: {chunk['metadata'].get('section_path')}):\n{chunk['text']}\n\n"
            
        system_instructions = """You are an expert facts-only Mutual Fund FAQ Assistant.
Your task is to answer the user's question using ONLY the provided contexts. 
Follow these strict rules:
1. Base your answer strictly and exclusively on the provided contexts. Do not assume or extrapolate. If the contexts do not contain the factual answer, reply with exactly: "I cannot find this information in the official documents."
2. Prohibit any advisory content. Do not recommend investing or not investing. Do not suggest one fund is better than another. Avoid any expressions of opinions.
3. Be concise and write at most 3 sentences.
4. Refuse requests containing personal identity information or financial advisory intent (e.g. asking for personal advice).
5. Do not include URLs or footers in your response (these will be added by a separate component)."""

        user_content = f"Context:\n{context_str}\n\nQuestion: {query}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.0
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            return answer.strip()
        except Exception as e:
            return f"Error generating answer: {str(e)}"

if __name__ == "__main__":
    # Quick sanity check with dummy data
    client = GroqClient()
    mock_chunks = [
        {
            "text": "HDFC Small Cap Fund Exit Load is 1% if redeemed within 1 year.",
            "metadata": {"section_path": "HDFC Small Cap Fund > Fund Metrics", "source_url": "https://test.com"}
        }
    ]
    ans = client.generate_answer("What is the exit load?", mock_chunks)
    print(f"Generated Response:\n{ans}")
