import requests
from bs4 import BeautifulSoup

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Let's print all paragraphs or elements containing a question mark '?'
    print("Searching for elements with '?'...")
    questions_found = 0
    for element in soup.find_all(text=True):
        parent_name = element.parent.name
        if parent_name in ["script", "style"]:
            continue
        text = element.strip()
        if "?" in text and len(text) > 10:
            print(f"Parent: {parent_name} -> {text}")
            questions_found += 1
            if questions_found >= 15:
                break
                
except Exception as e:
    print(f"Error: {e}")
