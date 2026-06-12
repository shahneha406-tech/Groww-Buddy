import requests
from bs4 import BeautifulSoup

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Print elements that contain FAQ or faq
    print("Searching for elements by class/id/tag...")
    for tag in soup.find_all(True):
        # check if 'faq' is in tag's classes or ID
        classes = tag.get("class", [])
        tag_id = tag.get("id", "")
        
        match = False
        if any("faq" in str(c).lower() for c in classes):
            match = True
        if "faq" in str(tag_id).lower():
            match = True
            
        if match:
            print(f"Tag: {tag.name}, Class: {classes}, ID: {tag_id}, Text snippet: {tag.text.strip()[:100]}")
            
    # Search for headings containing FAQ
    print("\nHeadings with 'FAQ' or 'Question':")
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        if "faq" in h.text.lower() or "question" in h.text.lower() or "frequently" in h.text.lower():
            print(f"Heading: {h.name} -> {h.text.strip()}")
            # print siblings/parent text to see what follow
            parent = h.parent
            print(f"Parent snippet: {parent.text.strip()[:300]}")
            
except Exception as e:
    print(f"Error: {e}")
