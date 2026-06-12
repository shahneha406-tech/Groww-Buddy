import json

with open("c:/Users/shahn/Groww Buddy/scratch/next_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Search for 'faq' anywhere in the JSON data keys
found = []
def search_faq(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            curr_path = f"{path}.{k}" if path else k
            if "faq" in k.lower():
                found.append((curr_path, type(v).__name__, str(v)[:200]))
            search_faq(v, curr_path)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            search_faq(item, f"{path}[{idx}]")

search_faq(data)

print(f"Found {len(found)} keys containing 'faq':")
for path, dtype, val_snippet in found:
    print(f"Path: {path} ({dtype}) -> {val_snippet}")
