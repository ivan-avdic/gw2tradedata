import requests
import json
import os
import time
from math import ceil

ITEM_LIST_PATH = "item_list.json"
OUTPUT_DIR = "OUTPUT_DIR = "current_snapshot_batches"historical_trends_batches"
ITEMS_PER_BATCH = 100
DELAY = 0.5

# Create or clear output directory
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
else:
    for f in os.listdir(OUTPUT_DIR):
        os.remove(os.path.join(OUTPUT_DIR, f))

with open(ITEM_LIST_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"🚀 Starting historical trend fetch for {len(items)} items...")
total_batches = ceil(len(items) / ITEMS_PER_BATCH)

for batch_index in range(total_batches):
    batch_start = batch_index * ITEMS_PER_BATCH
    batch_items = items[batch_start: batch_start + ITEMS_PER_BATCH]
    batch_data = []

    print(f"\n📦 Batch {batch_index + 1}/{total_batches} - {len(batch_items)} items")

    for i, item in enumerate(batch_items, start=1):
        item_id = item["item_id"]
        item_name = item["item_name"]
        url = f"https://www.gw2tp.com/api/trends?id={item_id}"

        print(f"  [{i}/{len(batch_items)}] {item_name} ({item_id})...", end="")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                trend = response.json()
                batch_data.append({
                    "item_id": item_id,
                    "item_name": item_name,
                    "trend": trend
                })
                print(" ✅")
            else:
                print(f" ❌ {response.status_code}")
        except Exception as e:
            print(f" ⚠️ {e}")

        time.sleep(DELAY)

    filename = f"historical_trends_{batch_index + 1:03}.json"
    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(batch_data, f, indent=2)
    print(f"📁 Saved {len(batch_data)} items to {filename}")
