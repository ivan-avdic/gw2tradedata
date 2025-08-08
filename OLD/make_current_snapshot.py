import requests
import json
import os
from datetime import datetime

# -------------------------------
# SETTINGS
# -------------------------------
ITEM_FILE = "item_list.json"
OUTPUT_FILE = "current_snapshot.json"
API_BASE = "https://api.guildwars2.com/v2/commerce/listings?ids="
TIMESTAMP = datetime.utcnow().isoformat() + "Z"

# -------------------------------
# STEP 1: Load item IDs from file
# -------------------------------
with open(ITEM_FILE, "r", encoding="utf-8") as f:
    item_list = json.load(f)

item_ids = [str(item["item_id"]) for item in item_list]
id_to_name = {item["item_id"]: item["item_name"] for item in item_list}

# -------------------------------
# STEP 2: Delete existing file (if any)
# -------------------------------
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

# -------------------------------
# STEP 3: Request listings from API
# -------------------------------
url = API_BASE + ",".join(item_ids)
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"API request failed: {response.status_code}")

results = response.json()

# -------------------------------
# STEP 4: Format and write data
# -------------------------------
entries = []
for item in results:
    top_buy = item.get("buys", [{}])[0] if item.get("buys") else {}
    top_sell = item.get("sells", [{}])[0] if item.get("sells") else {}

    entry = {
        "item_id": item["id"],
        "item_name": id_to_name.get(item["id"], "Unknown"),
        "timestamp": TIMESTAMP,
        "top_buy_price": top_buy.get("unit_price"),
        "top_buy_quantity": top_buy.get("quantity", 0),
        "top_sell_price": top_sell.get("unit_price"),
        "top_sell_quantity": top_sell.get("quantity", 0),
        "raw_buys": item.get("buys", []),
        "raw_sells": item.get("sells", [])
    }
    entries.append(entry)

# Write fresh file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2)

print(f"✔ Created new file {OUTPUT_FILE} with {len(entries)} items.")

