import requests
import json
import os
import time

ITEM_LIST_PATH = "item_list.json"
OUTPUT_FILE = "historical_trends.json"
DELAY = 0.5  # seconds between requests

# Load items
with open(ITEM_LIST_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

# Remove old file if exists
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

all_trends = []

# Iterate and collect trend data
for i, item in enumerate(items):
    item_id = item["item_id"]
    item_name = item["item_name"]
    url = f"https://www.gw2tp.com/api/trends?id={item_id}"
    print(f"[{i+1}/{len(items)}] Fetching trend for {item_name} ({item_id})")

    response = requests.get(url)
    if response.status_code == 200:
        trend = response.json()
        all_trends.append({
            "item_id": item_id,
            "item_name": item_name,
            "trend": trend
        })
    else:
        print(f"⚠️ Failed to fetch trend for {item_name} (ID {item_id})")

    time.sleep(DELAY)

# Save final output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_trends, f, indent=2)

print(f"✅ Historical trend data written to {OUTPUT_FILE} for {len(all_trends)} items.")

