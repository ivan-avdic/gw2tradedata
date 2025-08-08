import requests
import json
import os
from datetime import datetime, timezone

ITEM_LIST_PATH = "item_list.json"
OUTPUT_FILE = "current_snapshot.json"
CHUNK_SIZE = 150

# Use timezone-aware UTC timestamp
TIMESTAMP = datetime.now(timezone.utc).isoformat()

# Load item list
with open(ITEM_LIST_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

item_id_map = {item["item_id"]: item["item_name"] for item in items}
item_ids = list(item_id_map.keys())

# Function to split item IDs into manageable chunks
def get_chunked_responses(ids, chunk_size):
    url_base = "https://api.guildwars2.com/v2/commerce/listings?ids="
    results = []
    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i + chunk_size]
        url = url_base + ",".join(map(str, chunk))
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code}")
        results.extend(response.json())
    return results

# Fetch snapshot data
snapshot_data = get_chunked_responses(item_ids, CHUNK_SIZE)

# Structure the output
output = []
for item in snapshot_data:
    top_buy = item.get("buys", [{}])[0]
    top_sell = item.get("sells", [{}])[0]
    output.append({
        "item_id": item["id"],
        "item_name": item_id_map.get(item["id"], "Unknown"),
        "timestamp": TIMESTAMP,
        "top_buy_price": top_buy.get("unit_price"),
        "top_sell_price": top_sell.get("unit_price"),
        "top_buy_quantity": top_buy.get("quantity", 0),
        "top_sell_quantity": top_sell.get("quantity", 0),
        "raw_buys": item.get("buys", []),
        "raw_sells": item.get("sells", [])
    })

# Save to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print(f"✅ Snapshot written to {OUTPUT_FILE} with {len(output)} entries.")

