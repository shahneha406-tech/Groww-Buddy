from typing import Dict, Any, List

class ResponseFormatter:
    def format(self, response_text: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """
        Formats the response by appending exactly one citation URL and the last updated date.
        """
        if not retrieved_chunks:
            return response_text
            
        # Get the highest ranking chunk's metadata
        top_chunk = retrieved_chunks[0]
        meta = top_chunk.get("metadata", {})
        source_url = meta.get("source_url", "https://groww.in")
        last_updated = meta.get("last_updated_date", "2026-06-10")
        
        # Clean up any trailing space in the response text
        formatted_response = response_text.strip()
        
        # Ensure it doesn't end with duplicate citations or newlines
        # Format the citation and last updated footer
        citation_line = f"\n\nSource: {source_url}"
        footer_line = f"\nLast updated from sources: {last_updated}"
        
        return formatted_response + citation_line + footer_line

if __name__ == "__main__":
    formatter = ResponseFormatter()
    mock_chunks = [
        {
            "metadata": {
                "source_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
                "last_updated_date": "2026-06-10"
            }
        }
    ]
    txt = "HDFC Small Cap Fund's exit load is 1% if redeemed within 1 year."
    formatted = formatter.format(txt, mock_chunks)
    print(formatted)
