#!/usr/bin/env python3
"""
Regenerate index.json from the actual category files.

This script walks through all category files and builds an accurate
index.json that reflects the current state of the data.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CATEGORIES_PATH = Path("production data/categories")


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """Save data to a JSON file with nice formatting."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def get_product_count(data: dict) -> int:
    """Get the product count from a category file."""
    # First check for products array
    if "products" in data:
        return len(data["products"])
    # Then check pageInfo
    return data.get("pageInfo", {}).get("totalResults", 0)


def build_category_tree():
    """Build the category tree from the file structure."""
    categories = {}

    # First pass: identify all top-level categories (directories in categories/)
    for item in sorted(CATEGORIES_PATH.iterdir()):
        if item.is_dir():
            cat_name = item.name
            cat_json = CATEGORIES_PATH / f"{cat_name}.json"

            # Load category metadata if it exists
            if cat_json.exists():
                cat_data = load_json(cat_json)
            else:
                cat_data = {}

            categories[cat_name] = {
                "id": cat_name,
                "name": cat_data.get("name", cat_name.replace("-", " ").title()),
                "slug": cat_name,
                "productCount": 0,
                "subcategories": []
            }

            # Scan for subcategory files
            subcat_files = []
            for sub_item in sorted(item.iterdir()):
                if sub_item.is_file() and sub_item.suffix == ".json":
                    subcat_files.append(sub_item)
                elif sub_item.is_dir():
                    # This is a nested subcategory directory
                    subcat_json = item / f"{sub_item.name}.json"
                    if subcat_json.exists():
                        subcat_data = load_json(subcat_json)
                        sub_entry = {
                            "id": f"{cat_name}/{sub_item.name}",
                            "name": subcat_data.get("name", sub_item.name.replace("-", " ").title()),
                            "slug": sub_item.name,
                            "productCount": get_product_count(subcat_data),
                            "path": f"/categories/{cat_name}/{sub_item.name}",
                            "subcategories": []
                        }

                        # Scan for sub-subcategory files
                        for subsub_item in sorted(sub_item.iterdir()):
                            if subsub_item.is_file() and subsub_item.suffix == ".json":
                                subsub_data = load_json(subsub_item)
                                subsub_count = get_product_count(subsub_data)
                                if subsub_count > 0:
                                    sub_entry["subcategories"].append({
                                        "id": f"{cat_name}/{sub_item.name}/{subsub_item.stem}",
                                        "name": subsub_data.get("name", subsub_item.stem.replace("-", " ").title()),
                                        "slug": subsub_item.stem,
                                        "productCount": subsub_count,
                                        "path": f"/categories/{cat_name}/{sub_item.name}/{subsub_item.stem}"
                                    })

                        # If no nested subcategories, remove the empty array
                        if not sub_entry["subcategories"]:
                            del sub_entry["subcategories"]

                        categories[cat_name]["subcategories"].append(sub_entry)
                        categories[cat_name]["productCount"] += sub_entry["productCount"]

            # Process flat subcategory files (files directly in the category directory)
            for sub_file in subcat_files:
                sub_data = load_json(sub_file)
                sub_count = get_product_count(sub_data)

                # Skip if this has a matching directory (already processed above)
                if (item / sub_file.stem).is_dir():
                    continue

                if sub_count > 0:
                    categories[cat_name]["subcategories"].append({
                        "id": f"{cat_name}/{sub_file.stem}",
                        "name": sub_data.get("name", sub_file.stem.replace("-", " ").title()),
                        "slug": sub_file.stem,
                        "productCount": sub_count,
                        "path": f"/categories/{cat_name}/{sub_file.stem}"
                    })
                    categories[cat_name]["productCount"] += sub_count

    # Handle special categories (top-level JSON files without directories)
    for json_file in sorted(CATEGORIES_PATH.glob("*.json")):
        if json_file.stem == "index":
            continue

        cat_name = json_file.stem
        if cat_name not in categories:
            cat_data = load_json(json_file)
            count = get_product_count(cat_data)
            if count > 0:
                categories[cat_name] = {
                    "id": cat_name,
                    "name": cat_data.get("name", cat_name.replace("-", " ").title()),
                    "slug": cat_name,
                    "productCount": count,
                    "subcategories": []
                }

    return categories


def main():
    """Main entry point."""
    print("Regenerating index.json...")

    categories = build_category_tree()

    # Calculate totals
    total_products = sum(cat["productCount"] for cat in categories.values())
    total_categories = len(categories)

    # Count all subcategories too
    def count_subcats(subcats):
        count = len(subcats)
        for sub in subcats:
            if "subcategories" in sub:
                count += count_subcats(sub["subcategories"])
        return count

    for cat in categories.values():
        total_categories += count_subcats(cat.get("subcategories", []))

    # Build the final index structure
    index = {
        "version": "1.0",
        "lastUpdated": datetime.now().isoformat(),
        "totalCategories": total_categories,
        "totalProducts": total_products,
        "categories": sorted(categories.values(), key=lambda x: x["name"])
    }

    # Save the index
    index_path = CATEGORIES_PATH / "index.json"
    save_json(index_path, index)

    print(f"✅ Generated index.json")
    print(f"   Total categories: {total_categories}")
    print(f"   Total products: {total_products}")

    # Print category summary
    print("\n📊 Category Summary:")
    for cat in index["categories"]:
        subcat_count = len(cat.get("subcategories", []))
        print(f"   {cat['name']}: {cat['productCount']} products, {subcat_count} subcategories")


if __name__ == "__main__":
    main()
