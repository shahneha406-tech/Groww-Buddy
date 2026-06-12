import json

with open("c:/Users/shahn/Groww Buddy/scratch/next_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

mf_data = data["props"]["pageProps"]["mfServerSideData"]

print("SCHEME NAME:", mf_data.get("scheme_name"))
print("AUM:", mf_data.get("aum"))
print("NAV:", mf_data.get("nav"), "as of", mf_data.get("nav_date"))
print("EXPENSE RATIO:", mf_data.get("expense_ratio"))
print("EXIT LOAD:", mf_data.get("exit_load"))
print("BENCHMARK:", mf_data.get("benchmark"), "/", mf_data.get("benchmark_name"))
print("MIN INVESTMENT:", mf_data.get("min_investment_amount"))
print("MIN SIP INVESTMENT:", mf_data.get("min_sip_investment"))
print("LAUNCH DATE:", mf_data.get("launch_date"))
print("RISK LEVEL:", mf_data.get("nfo_risk"))  # or risk rating from simple_return?
print("LOCK IN:", mf_data.get("lock_in"))

print("\n--- FUND MANAGERS ---")
for m in mf_data.get("fund_manager_details", []):
    print(f"Name: {m.get('person_name')}")
    print(f"Education: {m.get('education')}")
    print(f"Experience: {m.get('experience')}")
    print(f"Managed since: {m.get('date_from')}")
    print(f"Funds managed:")
    for fm in m.get("funds_managed", []):
        print(f"  - {fm.get('scheme_name')} (code: {fm.get('scheme_code')})")

print("\n--- FIRST 5 HOLDINGS ---")
for h in mf_data.get("holdings", [])[:5]:
    print(f"Company: {h.get('company_name')}, Nature: {h.get('nature_name')}, Sector: {h.get('sector_name')}, Instrument: {h.get('instrument_name')}, Rating: {h.get('rating')}, Corpus %: {h.get('corpus_per')}")
