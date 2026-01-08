#!/usr/bin/env python3
"""
Add PLP tile type to all product data.

This script adds a 'plpTileType' field to products that determines
how they're displayed on Product Listing Pages (PLP).

Tile types:
- feature: Large, prominent tiles (appliances, home-decor, furniture)
- small: Medium-sized tiles (automotive, tools, outdoor, garage, storage)
- icon: Compact icon tiles (everything else)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Set

CATEGORIES_PATH = Path("production data/categories")
PRODUCTS_PATH = Path("production data/products")

# Category to tile type mapping
FEATURE_CATEGORIES = {"appliances", "home-decor", "furniture"}
SMALL_CATEGORIES = {"automotive", "tools", "outdoor", "outdoors", "garage", "storage"}
# Everything else defaults to "icon"


def get_tile_type(category_slug: str) -> str:
    """Determine tile type based on category."""
    # Extract the top-level category (first part of the path)
    top_level = category_slug.split("/")[0] if "/" in category_slug else category_slug

    if top_level in FEATURE_CATEGORIES:
        return "feature"
    elif top_level in SMALL_CATEGORIES:
        return "small"
    else:
        return "icon"


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """Save data to a JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def build_product_category_map() -> Dict[str, str]:
    """Build a mapping of product IDs to their category slugs."""
    product_to_category = {}

    def process_category_file(file_path: Path, category_id: str):
        """Process a single category file."""
        try:
            data = load_json(file_path)
            products = data.get("products", [])
            for product in products:
                product_id = product.get("productId")
                if product_id:
                    product_to_category[product_id] = category_id
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")

    def walk_category_dir(dir_path: Path, parent_id: str = ""):
        """Recursively walk category directories."""
        for item in sorted(dir_path.iterdir()):
            if item.is_file() and item.suffix == ".json":
                if item.name == "index.json":
                    continue
                category_id = parent_id if parent_id else item.stem
                process_category_file(item, category_id)
            elif item.is_dir():
                new_parent = f"{parent_id}/{item.name}" if parent_id else item.name
                walk_category_dir(item, new_parent)

    walk_category_dir(CATEGORIES_PATH)
    return product_to_category


def update_product_details(product_to_category: Dict[str, str]) -> int:
    """Update all product details.json files with plpTileType."""
    updated = 0

    for product_dir in sorted(PRODUCTS_PATH.iterdir()):
        if not product_dir.is_dir():
            continue

        details_file = product_dir / "details.json"
        if not details_file.exists():
            continue

        try:
            data = load_json(details_file)
            product_id = data.get("productId", product_dir.name)

            # Determine tile type based on category
            category = product_to_category.get(product_id, "other")
            tile_type = get_tile_type(category)

            # Add plpTileType field
            data["plpTileType"] = tile_type
            data["lastUpdated"] = datetime.now().isoformat()

            save_json(details_file, data)
            updated += 1

        except Exception as e:
            print(f"  Error updating {details_file}: {e}")

    return updated


def update_category_files() -> int:
    """Update all category JSON files to add plpTileType to products."""
    updated = 0

    def process_file(file_path: Path, category_id: str):
        """Process a single category file."""
        nonlocal updated
        try:
            data = load_json(file_path)
            products = data.get("products", [])

            if not products:
                return

            tile_type = get_tile_type(category_id)
            modified = False

            for product in products:
                if "plpTileType" not in product or product["plpTileType"] != tile_type:
                    product["plpTileType"] = tile_type
                    modified = True

            if modified:
                data["lastUpdated"] = datetime.now().isoformat()
                save_json(file_path, data)
                updated += 1

        except Exception as e:
            print(f"  Error processing {file_path}: {e}")

    def walk_category_dir(dir_path: Path, parent_id: str = ""):
        """Recursively walk category directories."""
        for item in sorted(dir_path.iterdir()):
            if item.is_file() and item.suffix == ".json":
                if item.name == "index.json":
                    continue
                category_id = parent_id if parent_id else item.stem
                process_file(item, category_id)
            elif item.is_dir():
                new_parent = f"{parent_id}/{item.name}" if parent_id else item.name
                walk_category_dir(item, new_parent)

    walk_category_dir(CATEGORIES_PATH)
    return updated


def print_summary(product_to_category: Dict[str, str]):
    """Print a summary of tile type distribution."""
    counts = {"feature": 0, "small": 0, "icon": 0}

    for product_id, category in product_to_category.items():
        tile_type = get_tile_type(category)
        counts[tile_type] += 1

    print("\nTile Type Distribution:")
    print(f"  feature: {counts['feature']} products (appliances, home-decor, furniture)")
    print(f"  small:   {counts['small']} products (automotive, tools, outdoor, garage, storage)")
    print(f"  icon:    {counts['icon']} products (everything else)")


def main():
    """Main entry point."""
    print("=" * 60)
    print("ADDING PLP TILE TYPE TO PRODUCTS")
    print("=" * 60)

    # Step 1: Build product-to-category mapping
    print("\n1. Building product-to-category mapping...")
    product_to_category = build_product_category_map()
    print(f"   Found {len(product_to_category)} products in category files")

    # Step 2: Update individual product details.json files
    print("\n2. Updating product details.json files...")
    products_updated = update_product_details(product_to_category)
    print(f"   Updated {products_updated} product files")

    # Step 3: Update category JSON files
    print("\n3. Updating category JSON files...")
    categories_updated = update_category_files()
    print(f"   Updated {categories_updated} category files")

    # Print summary
    print_summary(product_to_category)

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
