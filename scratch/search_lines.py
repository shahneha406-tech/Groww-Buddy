import requests

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers, timeout=10)
lines = response.text.split("\n")

print("Lines containing 'faq':")
for i, line in enumerate(lines):
    if "faq" in line.lower():
        print(f"Line {i} ({len(line)} chars): {line.strip()[:200]}")

print("\nLines containing 'question':")
for i, line in enumerate(lines):
    if "question" in line.lower():
        print(f"Line {i} ({len(line)} chars): {line.strip()[:200]}")
