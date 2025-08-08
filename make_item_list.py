import requests
from bs4 import BeautifulSoup
import json
import os
import time

BASE_URL = "https://www.gw2bltc.com/en/tp/search"
PARAMS = {
    "profit-pct-min": "20",
    "profit-pct-max": "40",
    "ipg": "200",
    "sort": "demand",
    "page": 1
}

OUTPUT_FILE = "item_list.json"

# Delete existing file if it exists
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

all_items = []

while True:
    print(f"Fetching page {PARAMS['page']}...")
    response = requests.get(BASE_URL, params=PARAMS)
    if response.status_code != 200:
        print(f"Error fetching page {PARAMS['page']}: {response.status_code}")
        break

    soup = BeautifulSoup(response.text, "html.parser")

    # Check for end condition
    if "No results were found." in soup.text:
        print("No more results found. Scraping complete.")
        break

    # Extract table rows
    rows = soup.find_all("tr")
    page_items = []

    for row in rows:
        img = row.find("img", attrs={"data-id": True})
        name_cell = row.find("td", class_="td-name")
        if img and name_cell:
            name_tag = name_cell.find("a")
            if name_tag:
                try:
                    item_id = int(img["data-id"])
                    item_name = name_tag.get_text(strip=True)
                    page_items.append({
                        "item_id": item_id,
                        "item_name": item_name
                    })
                except ValueError:
                    continue

    print(f" → Found {len(page_items)} items on page {PARAMS['page']}")
    all_items.extend(page_items)

    # Increment page
    PARAMS["page"] += 1

    # Optional: Respect server load
    time.sleep(1)

# Save to JSON
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_items, f, indent=2)

print(f"✅ Finished. Total items scraped: {len(all_items)}")
print(f"📁 Saved to: {OUTPUT_FILE}")
