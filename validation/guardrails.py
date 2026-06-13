import os
import re
import requests
import time
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
        greetings_exact = {"hi", "hello", "hey", "help", "greetings", "good morning", "good afternoon", "good evening"}
        greetings_prefixes = ["hi ", "hello ", "hey ", "good morning ", "good afternoon ", "good evening ", "who are you", "what are you", "what can you do"]
        if query_lower in greetings_exact or any(query_lower.startswith(p) for p in greetings_prefixes):
            return "greetings"

        # 2. Quick Heuristic Scan for advisory
        for pattern in self.advisory_keywords:
            if re.search(pattern, query_lower):
                return "advisory"

        # 3. LLM Classifier (using Groq API)
        if not self.api_key:
            # Safe default fallback if no key is present (rely on heuristics)
            return "factual"

        system_instructions = """You are an expert query classifier for a mutual fund FAQ assistant.
Your task is to classify the user's query into EXACTLY one of four categories: "factual", "advisory", "greetings", or "out-of-scope".

Categories:
- "greetings": The user is saying hello, greeting the assistant, or asking who/what the assistant is.
- "advisory": The user is asking for financial advice, recommendations, suggestions on where to invest, comparative performance opinions, or portfolio building planning.
- "out-of-scope": The user is asking about topics completely unrelated to mutual funds or finance (e.g. general knowledge, programming, baking, companies outside mutual funds like Next Leap, sports, etc.).
- "factual": The user is asking for specific data points, facts, rules, or details directly available from mutual fund documents (e.g., fund managers, exit load, expense ratio, NAV, launch date, assets under management, holdings list, etc.).

Examples:
Query: "Hi there!" -> greetings
Query: "what can you do?" -> greetings
Query: "Should I invest in HDFC Small Cap Fund?" -> advisory
Query: "Which fund has better returns: HDFC Mid-Cap or HDFC Top 100?" -> advisory
Query: "Is HDFC Defence Fund a good choice for short term?" -> advisory
Query: "Help me build an HDFC mutual fund portfolio." -> advisory
Query: "Which of these funds has the lowest risk for investment?" -> advisory
Query: "What is Next Leap?" -> out-of-scope
Query: "How do you make a chocolate cake?" -> out-of-scope
Query: "Write a python function to binary search an array." -> out-of-scope
Query: "What is the capital of France?" -> out-of-scope
Query: "What is the exit load of HDFC Defence Fund?" -> factual
Query: "Who is the fund manager of HDFC Defence Fund?" -> factual
Query: "What is the expense ratio of HDFC Defence Fund?" -> factual
Query: "What is the benchmark of HDFC Defence Fund?" -> factual
Query: "When was HDFC Defence Fund launched?" -> factual

Respond with EXACTLY one word: "factual", "advisory", "greetings", or "out-of-scope". Do not include any other explanation, text, or punctuation. Output must be lowercase."""

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

        max_retries = 5
        backoff = 2
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=8)
                if response.status_code == 429:
                    print(f"      [RATE LIMIT] classify_intent: 429 received. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"[DEBUG] Guardrails classify_intent exception: {e}")
                    import traceback
                    traceback.print_exc()
                    return "factual"
                time.sleep(backoff)
                backoff *= 2

        if not response:
            return "factual"

        try:
            result = response.json()["choices"][0]["message"]["content"].strip().lower()
            if "advisory" in result:
                return "advisory"
            elif "greetings" in result:
                return "greetings"
            elif "out-of-scope" in result or "out_of_scope" in result or "scope" in result:
                return "out-of-scope"
            return "factual"
        except Exception as e:
            print(f"[DEBUG] Guardrails parsing exception: {e}")
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
