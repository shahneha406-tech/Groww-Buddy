import re
from typing import List, Dict, Any, Tuple

class ResponseValidator:
    def __init__(self):
        # Keywords indicating advisory, opinionated, or non-factual generation
        self.advisory_keywords = [
            r"\brecommend", r"\bsuggest\b", r"\badvisable\b", r"\bshould\s*(?:buy|invest|sell|avoid)\b",
            r"\bforecast\b", r"\bpredict\b", r"\bbest\s*(?:fund|choice|option|investment)\b",
            r"\bguarantee", r"\bwould\s*suggest\b", r"\byou\s*must\b", r"\bhighly\s*recommended\b"
        ]

    def count_sentences(self, text: str) -> int:
        """
        Counts the number of sentences in the text.
        Splits by sentence ending punctuation (., !, ?) followed by space or end of string.
        """
        # Clean double newlines and normalize spaces
        text = re.sub(r'\s+', ' ', text.strip())
        # Split using lookbehind assertion
        sentences = [s for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        return len(sentences)

    def validate(self, response: str, retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Validates the generated response.
        Returns:
            (is_valid: bool, validated_response: str)
        """
        # 1. Fallback / Empty Check
        if not response or "error" in response.lower():
            return False, "I cannot find this information in the official documents."

        # 2. Sentence Length Check (max 3 sentences)
        sentence_count = self.count_sentences(response)
        if sentence_count > 3:
            return False, "I cannot find this information in the official documents."

        # 3. Citation Check
        # Check if the retrieved chunks actually have valid metadata and source URLs
        has_citation = False
        for chunk in retrieved_chunks:
            meta = chunk.get("metadata", {})
            if meta.get("source_url"):
                has_citation = True
                break
        if not has_citation:
            return False, "I cannot find this information in the official documents."

        # 4. Advisory/PII Check
        response_lower = response.lower()
        for pattern in self.advisory_keywords:
            if re.search(pattern, response_lower):
                return False, "I am a factual FAQ assistant and cannot provide investment advice or recommendations. Please consult a SEBI-registered advisor."

        # 5. Check if LLM outputted its own fallback refusal
        if "cannot find" in response_lower or "not mentioned in" in response_lower or "no information" in response_lower:
            return True, "I cannot find this information in the official documents."

        return True, response

if __name__ == "__main__":
    validator = ResponseValidator()
    
    # Test cases
    test_context = [{"metadata": {"source_url": "https://groww.in"}}]
    
    # Valid test case
    t1 = "HDFC Small Cap Fund Direct Growth is managed by Chirag Setalvad. It was launched in 2013."
    print(f"t1 (valid?): {validator.validate(t1, test_context)}")
    
    # Invalid test case: too long
    t2 = "HDFC Small Cap Fund is good. It is managed by Chirag Setalvad. It was launched in 2013. You should buy it."
    print(f"t2 (valid?): {validator.validate(t2, test_context)}")

    # Invalid test case: advisory
    t3 = "You should invest in HDFC Small Cap Fund because it is the best fund."
    print(f"t3 (valid?): {validator.validate(t3, test_context)}")
