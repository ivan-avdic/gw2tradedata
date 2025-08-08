import requests
import json
import os
from time import sleep

# -------------------------------
# SETTINGS
# -------------------------------
ITEM_FILE = "item_list.json"
OUTPUT_FILE = "historical_trends.json"
API_TEMPLATE = "https://www.gw2tp.com/api/trends?id={}"

# -------------------------------
# STEP 1: Load item IDs from file
# -------------------------------
with open(ITEM_FILE, "r", encoding="utf-8") as f:
    item_list = json.load(f)

# -------------------------------
# STEP 2: Delete existing file (if any)
# -------------------------------
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

# -------------------------------
# STEP 3: Request trend data per item
# -------------------------------
all_trends = []

for item in item_list:
    item_id = item["item_id"]
    item_name = item["item_name"]
    url = API_TEMPLATE.format(item_id)
    response = requests.get(url)

    if response.status_code != 200:
        print(f"⚠️ Failed for {item_name} ({item_id}) - Status {response.status_code}")
        continue

    try:
        trend_data = response.json()
    except json.JSONDecodeError:
        print(f"⚠️ JSON error for {item_name} ({item_id})")
        continue

    all_trends.append({
        "item_id": item_id,
        "item_name": item_name,
        "trend": trend_data
    })

    sleep(0.5)  # respect server load

# Write fresh file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_trends, f, indent=2)

print(f"✔ Created new file {OUTPUT_FILE} with {len(all_trends)} items.")

