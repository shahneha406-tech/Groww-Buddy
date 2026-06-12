import requests
from bs4 import BeautifulSoup
import json

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
soup = BeautifulSoup(response.text, "html.parser")

for idx, s in enumerate(soup.find_all("script", type="application/ld+json")):
    try:
        data = json.loads(s.string)
        print(f"JSON-LD script {idx}: @context={data.get('@context')}, @type={data.get('@type')}")
        if data.get("@type") == "FAQPage":
            print("FOUND FAQ PAGE!")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error parsing script {idx}: {e}")
