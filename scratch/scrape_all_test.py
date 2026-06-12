import requests
from bs4 import BeautifulSoup
import json

urls = {
    "hdfc_mid_cap": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "hdfc_large_cap": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "hdfc_small_cap": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "hdfc_gold_foh": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "hdfc_defence": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for name, url in urls.items():
    print(f"\n==================== {name} ====================")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        next_data = soup.find("script", id="__NEXT_DATA__")
        if next_data:
            js = json.loads(next_data.text)
            mf_data = js.get("props", {}).get("pageProps", {}).get("mfServerSideData", {})
            print("Scheme Name in JSON:", mf_data.get("scheme_name"))
            print("NAV:", mf_data.get("nav"), "date:", mf_data.get("nav_date"))
            print("Expense Ratio:", mf_data.get("expense_ratio"))
            print("Exit Load:", mf_data.get("exit_load"))
            print("AUM:", mf_data.get("aum"))
            print("Description length:", len(mf_data.get("description", "")) if mf_data.get("description") else 0)
        else:
            print("No NEXT_DATA found!")
    except Exception as e:
        print("Error:", e)
