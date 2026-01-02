#!/usr/bin/env python3
"""
Generate combined "all products" files for ALL categories.

This creates:
1. For categories WITH subcategory directories:
   - appliances/refrigerators/_all.json (combines all subcategory products)

2. For categories WITHOUT subcategory directories (flat):
   - appliances/_all.json (combines all direct subcategory files like dishwashers.json, microwaves.json)

This makes it easy for an iOS app to load everything at once and filter client-side.
"""

import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

CATEGORIES_PATH = Path("production data/categories")


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """Save data to a JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def compute_featured_brands(products: list, max_brands: int = 6) -> list:
    """Compute featured brands from products."""
    brand_counts = defaultdict(int)
    for product in products:
        brand = product.get("brand", "")
        if brand:
            brand_counts[brand] += 1

    sorted_brands = sorted(brand_counts.items(), key=lambda x: (-x[1], x[0]))

    featured = []
    for brand_name, count in sorted_brands[:max_brands]:
        slug = brand_name.lower().replace(" ", "-").replace("&", "-")
        featured.append({
            "brandId": slug,
            "brandName": brand_name,
            "logoUrl": f"images/brands/{slug}.svg",
            "count": count
        })

    return featured


def generate_subdir_all_products(category_dir: Path, subcat_dir: Path):
    """Generate an _all.json file for a subcategory directory (nested structure)."""
    all_products = []
    subcategories = []

    # Collect products from all JSON files in the directory
    for json_file in sorted(subcat_dir.glob("*.json")):
        if json_file.stem.startswith("_"):
            continue  # Skip meta files

        data = load_json(json_file)
        products = data.get("products", [])

        if products:
            subcategories.append({
                "slug": json_file.stem,
                "name": data.get("name", json_file.stem.replace("-", " ").title()),
                "productCount": len(products)
            })
            all_products.extend(products)

    if not all_products:
        return None

    # Get category info from parent JSON if it exists
    parent_json = category_dir / f"{subcat_dir.name}.json"
    if parent_json.exists():
        parent_data = load_json(parent_json)
        category_name = parent_data.get("name", subcat_dir.name.replace("-", " ").title())
        breadcrumbs = parent_data.get("breadcrumbs", [])
    else:
        category_name = subcat_dir.name.replace("-", " ").title()
        breadcrumbs = []

    # Build the _all.json structure
    category_path = f"{category_dir.name}/{subcat_dir.name}"
    all_data = {
        "categoryId": category_path,
        "name": category_name,
        "slug": subcat_dir.name,
        "path": f"/categories/{category_path}",
        "version": "1.0",
        "lastUpdated": datetime.now().isoformat(),
        "breadcrumbs": breadcrumbs,
        "pageInfo": {
            "totalResults": len(all_products)
        },
        "featuredBrands": compute_featured_brands(all_products),
        "filterOptions": {
            "subcategories": sorted(subcategories, key=lambda x: -x["productCount"])
        },
        "products": all_products
    }

    # Save the file
    all_file = subcat_dir / "_all.json"
    save_json(all_file, all_data)

    return {
        "path": str(all_file.relative_to(CATEGORIES_PATH)),
        "products": len(all_products),
        "subcategories": len(subcategories)
    }


def generate_category_all_products(category_dir: Path):
    """Generate an _all.json file for a top-level category (flat structure)."""
    all_products = []
    subcategories = []

    # Collect products from all JSON files directly in the category directory
    for json_file in sorted(category_dir.glob("*.json")):
        if json_file.stem.startswith("_"):
            continue  # Skip meta files

        # Skip if there's a matching subdirectory (those are handled separately)
        if (category_dir / json_file.stem).is_dir():
            continue

        data = load_json(json_file)
        products = data.get("products", [])

        if products:
            subcategories.append({
                "slug": json_file.stem,
                "name": data.get("name", json_file.stem.replace("-", " ").title()),
                "productCount": len(products)
            })
            all_products.extend(products)

    # Also include products from subdirectory _all.json files
    for subdir in sorted(category_dir.iterdir()):
        if subdir.is_dir():
            subdir_all = subdir / "_all.json"
            if subdir_all.exists():
                data = load_json(subdir_all)
                products = data.get("products", [])
                if products:
                    subcategories.append({
                        "slug": subdir.name,
                        "name": data.get("name", subdir.name.replace("-", " ").title()),
                        "productCount": len(products)
                    })
                    all_products.extend(products)
            else:
                # Check for parent JSON with products
                parent_json = category_dir / f"{subdir.name}.json"
                if parent_json.exists():
                    data = load_json(parent_json)
                    # If the parent has no products but subdirectory has files, aggregate them
                    if not data.get("products"):
                        subdir_products = []
                        for json_file in subdir.glob("*.json"):
                            if not json_file.stem.startswith("_"):
                                subdata = load_json(json_file)
                                subdir_products.extend(subdata.get("products", []))
                        if subdir_products:
                            subcategories.append({
                                "slug": subdir.name,
                                "name": data.get("name", subdir.name.replace("-", " ").title()),
                                "productCount": len(subdir_products)
                            })
                            all_products.extend(subdir_products)

    if not all_products:
        return None

    # Build the _all.json structure
    all_data = {
        "categoryId": category_dir.name,
        "name": category_dir.name.replace("-", " ").title(),
        "slug": category_dir.name,
        "path": f"/categories/{category_dir.name}",
        "version": "1.0",
        "lastUpdated": datetime.now().isoformat(),
        "breadcrumbs": [
            {"label": "Home", "url": "/"},
            {"label": category_dir.name.replace("-", " ").title(), "url": f"/{category_dir.name}"}
        ],
        "pageInfo": {
            "totalResults": len(all_products)
        },
        "featuredBrands": compute_featured_brands(all_products),
        "filterOptions": {
            "subcategories": sorted(subcategories, key=lambda x: -x["productCount"])
        },
        "products": all_products
    }

    # Save the file
    all_file = category_dir / "_all.json"
    save_json(all_file, all_data)

    return {
        "path": str(all_file.relative_to(CATEGORIES_PATH)),
        "products": len(all_products),
        "subcategories": len(subcategories)
    }


def main():
    """Generate _all.json files for all categories."""
    print("=" * 60)
    print("GENERATING ALL-PRODUCTS FILES")
    print("=" * 60)

    generated = []

    # First pass: Generate _all.json for nested subcategory directories
    print("\n📁 Processing nested subcategory directories...")
    for category_dir in sorted(CATEGORIES_PATH.iterdir()):
        if not category_dir.is_dir():
            continue

        for subcat_dir in sorted(category_dir.iterdir()):
            if not subcat_dir.is_dir():
                continue

            # Check if this directory has product JSON files
            json_files = [f for f in subcat_dir.glob("*.json") if not f.stem.startswith("_")]
            if not json_files:
                continue

            result = generate_subdir_all_products(category_dir, subcat_dir)
            if result:
                print(f"  ✅ {result['path']}: {result['products']} products, {result['subcategories']} subcategories")
                generated.append(result)

    # Second pass: Generate _all.json for top-level categories
    print("\n📁 Processing top-level categories...")
    for category_dir in sorted(CATEGORIES_PATH.iterdir()):
        if not category_dir.is_dir():
            continue

        result = generate_category_all_products(category_dir)
        if result:
            print(f"  ✅ {result['path']}: {result['products']} products, {result['subcategories']} subcategories")
            generated.append(result)

    print("\n" + "=" * 60)
    print(f"Generated {len(generated)} _all.json files")
    print("=" * 60)

    # Print summary table
    print("\n📊 Summary of _all.json files:")
    print("-" * 60)
    print(f"{'File Path':<45} {'Products':>8} {'Filters':>7}")
    print("-" * 60)
    for result in sorted(generated, key=lambda x: x['path']):
        print(f"{result['path']:<45} {result['products']:>8} {result['subcategories']:>7}")

    # Print usage instructions
    print("\n" + "=" * 60)
    print("📱 iOS APP USAGE")
    print("=" * 60)
    print("""
To load ALL products for a category with filter pills:

1. Fetch the _all.json file:
   - All appliances: appliances/_all.json
   - All refrigerators: appliances/refrigerators/_all.json
   - All tools: tools/_all.json
   - All saws: tools/saws/_all.json

2. Use filterOptions.subcategories for filter pills:
   {
     "filterOptions": {
       "subcategories": [
         {"slug": "french-door", "name": "French Door", "productCount": 78},
         {"slug": "side-by-side", "name": "Side By Side", "productCount": 31},
         ...
       ]
     }
   }

3. Filter products client-side by the 'subcategory' field on each product
""")


if __name__ == "__main__":
    main()
