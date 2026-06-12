import json

with open("c:/Users/shahn/Groww Buddy/scratch/next_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

mf_data = data["props"]["pageProps"]["mfServerSideData"]

print("ALL TOP-LEVEL KEYS:")
print(sorted(mf_data.keys()))
