import requests
from bs4 import BeautifulSoup

url = "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.text)}")
    soup = BeautifulSoup(response.text, "html.parser")
    # Print the title tag to see if it loaded the actual page
    print(f"Title: {soup.title.text if soup.title else 'No Title'}")
    
    # Check if there is any heading or body content
    h1 = soup.find("h1")
    print(f"H1: {h1.text if h1 else 'No H1'}")
    
    # Save a small snippet to see the HTML structure
    with open("scratch_response.html", "w", encoding="utf-8") as f:
        f.write(response.text[:2000])
except Exception as e:
    print(f"Error: {e}")
