import requests
from bs4 import BeautifulSoup

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
html = response.text.lower()

terms = ["faq", "frequently", "question", "answer"]
for term in terms:
    count = html.count(term)
    print(f"Term '{term}' count in raw HTML: {count}")
