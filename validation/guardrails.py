import os
import re
import requests
from typing import Dict, Any

class GuardrailsManager:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.model_name = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

        # Heuristic keywords indicating advisory or comparison intent
        self.advisory_keywords = [
            r"\brecommend", r"\bportfolio\b", r"\bsuggest\b",
            r"\bshould\s*i\s*(?:buy|invest|sell|avoid)\b",
            r"\bwhich\s*(?:is|would\s*be)\s*better\b",
            r"\bwhich\s*fund\s*(?:should|to\s*invest)\b",
            r"\bcompare\b", r"\bcomparison\b",
            r"\badvice\b", r"\badvisable\b",
            r"\bwhere\s*should\s*i\b",
            r"\bbest\s*(?:fund|choice|option|investment)\b"
        ]

    def detect_pii(self, query: str) -> bool:
        """
        Scans query for Aadhaar, PAN, emails, bank accounts, and phone numbers.
        Returns True if PII is detected, else False.
        """
        # Aadhaar: 12-digit number (optionally with spaces or hyphens)
        aadhaar_pattern = r"\b\d{4}[\s\-]*\d{4}[\s\-]*\d{4}\b"
        # PAN: 5 letters, 4 digits, 1 letter
        pan_pattern = r"\b[A-Za-z]{5}\d{4}[A-Za-z]\b"
        # Email address
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        # Phone: Indian 10-digit formats (with optional +91 or 0 prefix)
        phone_pattern = r"\b(?:(?:\+|0{0,2})91[\s\-]*)?[6789]\d{9}\b"
        # Bank Account: 9 to 18 digits
        bank_pattern = r"\b\d{9,18}\b"

        # Combine checks (Aadhaar, PAN, email, phone)
        # For bank account, we verify it doesn't match normal short numbers or launch dates
        # standard 9-18 digits check
        for pattern in [aadhaar_pattern, pan_pattern, email_pattern, phone_pattern]:
            if re.search(pattern, query):
                return True
                
        # Bank account check (ensure it is not a year, NAV, or amount like 38,000)
        # Standard check: sequence of 9+ digits
        if re.search(bank_pattern, query):
            # Exclude strings that look like dates or formatting commas
            cleaned = re.sub(r'[\s,\.\-]', '', query)
            if re.search(r'\b\d{9,18}\b', cleaned):
                return True

        return False

    def classify_intent(self, query: str) -> str:
        """
        Classifies user intent as 'factual', 'advisory', 'greetings', or 'out-of-scope'.
        Returns: 'factual', 'advisory', 'greetings', or 'out-of-scope'.
        """
        query_lower = query.lower().strip()

        # 1. Quick check for greetings/help
        greetings_keywords = ["hi", "hello", "hey", "help", "good morning", "good afternoon", "good evening", "who are you", "what are you", "what can you do"]
        if query_lower in greetings_keywords or any(query_lower.startswith(g + " ") for g in greetings_keywords) or query_lower == "help":
            return "greetings"

        # 2. Quick Heuristic Scan for advisory
        for pattern in self.advisory_keywords:
            if re.search(pattern, query_lower):
                return "advisory"

        # 3. LLM Classifier (using Groq API)
        if not self.api_key:
            # Safe default fallback if no key is present (rely on heuristics)
            return "factual"

        system_instructions = """You are an expert query classifier for a mutual fund facts database.
Your task is to classify the user's query into one of four categories: "factual", "advisory", "greetings", or "out-of-scope".
- "factual": The user is asking for specific data points, facts, rules, or information related to mutual funds, investing, or finance (specifically HDFC mutual funds, expense ratios, NAV, exit load, fund managers, holdings list, etc.).
- "advisory": The user is asking for financial advice, recommendations, opinions, fund comparisons, suggestions on where to invest, or portfolio planning.
- "greetings": The user is greeting the assistant (e.g., "hi", "hello", "hey", "good morning") or asking who the assistant is / what it does.
- "out-of-scope": The user is asking about topics completely unrelated to mutual funds, investing, or finance (e.g., "What is Next Leap?", "How to make tea?", general knowledge, coding, politics, history, etc.).

Respond with EXACTLY one word: "factual", "advisory", "greetings", or "out-of-scope". Do not write any other explanation or punctuation."""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": f"Query: {query}"}
            ],
            "temperature": 0.0
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=5)
            response.raise_for_status()
            result = response.json()["choices"][0]["message"]["content"].strip().lower()
            if "advisory" in result:
                return "advisory"
            elif "greetings" in result:
                return "greetings"
            elif "out-of-scope" in result or "out_of_scope" in result or "scope" in result:
                return "out-of-scope"
            return "factual"
        except Exception:
            # Fallback to factual if API fails but heuristics are clean
            return "factual"

if __name__ == "__main__":
    # Sanity checks
    manager = GuardrailsManager()
    
    # Test PII
    print("PII test 1 (email):", manager.detect_pii("Contact me at test@example.com"))
    print("PII test 2 (PAN):", manager.detect_pii("My PAN is ABCDE1234F"))
    print("PII test 3 (Normal):", manager.detect_pii("What is the exit load?"))
    
    # Test heuristics
    print("Intent test 1 (should buy):", manager.classify_intent("Should I buy HDFC Defence Fund?"))
    print("Intent test 2 (normal):", manager.classify_intent("Who is the fund manager of HDFC Defence Fund?"))
