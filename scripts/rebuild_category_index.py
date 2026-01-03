#!/usr/bin/env python3
"""
Rebuild the category index.json with accurate product counts.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CATEGORIES_PATH = Path("production data/categories")


def get_category_counts():
    """Get product counts for all category files."""
    counts = {}

    for json_file in CATEGORIES_PATH.rglob("*.json"):
        if json_file.name.startswith("_") or json_file.name == "index.json":
            continue

        try:
            data = json.loads(json_file.read_text())
            products = data.get("products", [])

            # Get relative path as category ID
            rel_path = json_file.relative_to(CATEGORIES_PATH)
            category_id = str(rel_path).replace(".json", "").replace("/", "/")
            counts[category_id] = len(products)
        except:
            pass

    return counts


def build_category_tree(counts):
    """Build hierarchical category structure."""
    # Group by top-level category
    top_level = defaultdict(list)

    for cat_id, count in counts.items():
        parts = cat_id.split("/")
        top = parts[0]
        top_level[top].append((cat_id, count))

    return top_level


def main():
    print("Rebuilding category index...")

    counts = get_category_counts()
    print(f"Found {len(counts)} category files")

    # Load existing index
    index_path = CATEGORIES_PATH / "index.json"
    index = json.loads(index_path.read_text())

    total_products = sum(counts.values())

    # Update counts in existing structure
    def update_category(cat, counts):
        cat_id = cat.get("id", "")
        if cat_id in counts:
            cat["productCount"] = counts[cat_id]

        # Update subcategories recursively
        for sub in cat.get("subcategories", []):
            update_category(sub, counts)

    # Check if we need to add furniture/outdoor
    furniture_cats = [c for c in index["categories"] if c["id"] == "furniture"]
    if furniture_cats:
        furniture = furniture_cats[0]
        outdoor_exists = any(s["id"] == "furniture/outdoor" for s in furniture.get("subcategories", []))
        if not outdoor_exists and "furniture/outdoor" in counts:
            furniture["subcategories"].append({
                "id": "furniture/outdoor",
                "name": "Outdoor",
                "slug": "outdoor",
                "productCount": counts.get("furniture/outdoor", 0),
                "path": "/categories/furniture/outdoor"
            })

    for cat in index["categories"]:
        update_category(cat, counts)

    # Update totals
    index["lastUpdated"] = datetime.now().isoformat()
    index["totalProducts"] = total_products

    # Write updated index
    index_path.write_text(json.dumps(index, indent=2))
    print(f"Updated index.json with {total_products} total products")


if __name__ == "__main__":
    main()
