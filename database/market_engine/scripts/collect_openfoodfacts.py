import json
import time
from pathlib import Path

import requests


BASE_URL = "https://world.openfoodfacts.org/api/v2/search"

OUTPUT_FILE = Path(
    "data/raw/openfoodfacts/openfoodfacts_india_raw.jsonl"
)

PAGE_SIZE = 10
MAX_PAGES_PER_CATEGORY = 3

CATEGORIES = [
    "muesli",
    "oats",
    "breakfast-cereals",
    "bread",
    "peanut-butter",
    "nut-butters",
    "milk",
    "yogurts",
    "snacks",
    "biscuits",
    "juices",
    "protein-foods",
]

FIELDS = [
    "code",
    "product_name",
    "brands",
    "categories_tags",
    "countries_tags",
    "nutriments",
    "ingredients_text",
    "allergens_tags",
    "labels_tags",
    "image_url",
    "last_modified_t",
]

HEADERS = {
    "User-Agent": "Jivanya/1.0 (food-market-engine project)"
}


def get_products(category, page):
    params = {
        "countries_tags_en": "india",
        "categories_tags": category,
        "page": page,
        "page_size": PAGE_SIZE,
        "fields": ",".join(FIELDS),
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def product_is_valid(product):
    code = product.get("code")
    name = product.get("product_name")

    return bool(code and name and name.strip())


def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing products so we don't create duplicate barcodes.
    existing_codes = set()

    if OUTPUT_FILE.exists():
        with OUTPUT_FILE.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    product = json.loads(line)
                    code = product.get("code")

                    if code:
                        existing_codes.add(str(code))
                except json.JSONDecodeError:
                    continue

    print("Starting Jivanya Open Food Facts collection...")
    print(f"Existing products: {len(existing_codes)}")
    print(f"Output: {OUTPUT_FILE}")
    print()

    total_saved = len(existing_codes)

    with OUTPUT_FILE.open("a", encoding="utf-8") as output:

        for category in CATEGORIES:

            print("=" * 60)
            print(f"Category: {category}")
            print("=" * 60)

            for page in range(1, MAX_PAGES_PER_CATEGORY + 1):

                print(f"Downloading page {page}...")

                try:
                    data = get_products(category, page)

                except requests.RequestException as error:

                    print(f"Request failed: {error}")
                    print("Waiting 10 seconds before retry...")

                    time.sleep(10)

                    try:
                        data = get_products(category, page)

                    except requests.RequestException as retry_error:

                        print(f"Retry failed: {retry_error}")
                        print("Skipping this page.")
                        continue

                products = data.get("products", [])

                if not products:
                    print("No more products in this category.")
                    break

                saved_this_page = 0

                for product in products:

                    if not product_is_valid(product):
                        continue

                    code = str(product["code"])

                    if code in existing_codes:
                        continue

                    output.write(
                        json.dumps(
                            product,
                            ensure_ascii=False
                        )
                        + "\n"
                    )

                    existing_codes.add(code)

                    saved_this_page += 1
                    total_saved += 1

                output.flush()

                print(
                    f"Saved {saved_this_page} new products "
                    f"(total: {total_saved})"
                )

                time.sleep(2)

    print()
    print("=" * 60)
    print("Collection completed.")
    print(f"Total unique products: {total_saved}")
    print(f"Raw dataset: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
