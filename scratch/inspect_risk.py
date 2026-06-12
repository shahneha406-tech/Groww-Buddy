import json

with open("c:/Users/shahn/Groww Buddy/scratch/next_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

mf_data = data["props"]["pageProps"]["mfServerSideData"]

print("simple_return risk keys/values:")
sr = mf_data.get("simple_return", {})
print("  risk:", sr.get("risk"))
print("  risk_rating:", sr.get("risk_rating"))

print("return_stats risk:")
rs = mf_data.get("return_stats", [{}])[0]
print("  risk:", rs.get("risk"))
print("  risk_rating:", rs.get("risk_rating"))
