import requests
import json
import os
from datetime import datetime, timezone
from math import ceil

ITEM_LIST_PATH = "item_list.json"
OUTPUT_DIR = "current_snapshot_batches"
CHUNK_SIZE = 40
BATCH_SIZE = 40  # Split output per this many items

# Create or clean output directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
else:
    for f in os.listdir(OUTPUT_DIR):
        os.remove(os.path.join(OUTPUT_DIR, f))

TIMESTAMP = datetime.now(timezone.utc).isoformat()

# Load item list
with open(ITEM_LIST_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

item_id_map = {item["item_id"]: item["item_name"] for item in items}
item_ids = list(item_id_map.keys())

def get_chunked_responses(ids, chunk_size):
    url_base = "https://api.guildwars2.com/v2/commerce/listings?ids="
    results = []

    total_chunks = (len(ids) + chunk_size - 1) // chunk_size
    print(f"🔄 Fetching {len(ids)} items in {total_chunks} chunks...")

    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i + chunk_size]
        url = url_base + ",".join(map(str, chunk))
        print(f"📡 Chunk {i // chunk_size + 1}/{total_chunks}")
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"❌ API request failed: {response.status_code}")
        results.extend(response.json())

    return results

print("🚀 Starting snapshot capture...")

snapshot_data = get_chunked_responses(item_ids, CHUNK_SIZE)
output = []

for i, item in enumerate(snapshot_data, start=1):
    item_id = item["id"]
    item_name = item_id_map.get(item_id, "Unknown")
    buys = item.get("buys", [])
    sells = item.get("sells", [])
    top_buy = buys[0] if buys else {"unit_price": 0, "quantity": 0}
    top_sell = sells[0] if sells else {"unit_price": 0, "quantity": 0}

    entry = {
        "item_id": item_id,
        "item_name": item_name,
        "timestamp": TIMESTAMP,
        "top_buy_price": top_buy["unit_price"],
        "top_sell_price": top_sell["unit_price"],
        "top_buy_quantity": top_buy["quantity"],
        "top_sell_quantity": top_sell["quantity"],
        "raw_buys": buys,
        "raw_sells": sells
    }

    output.append(entry)

# Split into batches
total_batches = ceil(len(output) / BATCH_SIZE)
for i in range(total_batches):
    batch = output[i * BATCH_SIZE: (i + 1) * BATCH_SIZE]
    filename = f"current_snapshot_{i+1:03}.json"
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)
    print(f"✅ Saved batch {i+1}/{total_batches}: {filename} ({len(batch)} items)")
