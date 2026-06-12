import requests
import re

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
text = response.text

# Find all occurrences of faq (case-insensitive) and print 100 chars before and after
for m in re.finditer(r'faq', text, re.IGNORECASE):
    start = max(0, m.start() - 100)
    end = min(len(text), m.end() + 100)
    print(f"Match at {m.start()}: ... {text[start:end]} ...\n")
