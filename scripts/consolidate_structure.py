#!/usr/bin/env python3
"""
Consolidate category data structure for optimal iOS app consumption.

This script:
1. Merges parent JSON products into appropriate subcategory files
2. Removes duplicate flat files when nested structure exists
3. Creates consistent structure across all categories
4. Updates product counts and metadata

Structure after consolidation:
- Categories with subcategories: Use directory structure, remove parent .json products
- Categories without subcategories: Keep as single .json file with products
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Optional

CATEGORIES_PATH = Path("production data/categories")


def slugify(name: str) -> str:
    """Convert a name to a URL-friendly slug."""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """Save data to a JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  ✅ Saved: {path}")


def get_product_subcategory_slug(product: dict) -> Optional[str]:
    """Determine which subcategory a product belongs to based on its title."""
    title = product.get("title", "").lower()
    subcategory = product.get("subcategory", "")

    # Refrigerator types
    if "french door" in title or "french-door" in title:
        return "french-door"
    if "side by side" in title or "side-by-side" in title:
        return "side-by-side"
    if "top freezer" in title or "top-freezer" in title:
        return "top-freezer"
    if "bottom freezer" in title or "bottom-freezer" in title:
        return "bottom-freezer"
    if "counter depth" in title or "counter-depth" in title:
        return "counter-depth"
    if "freezerless" in title:
        return "freezerless"
    if "mini fridge" in title or "compact" in title or "mini refrigerator" in title:
        return "mini-fridges"

    # Saw types
    if "table saw" in title:
        return "table-saws"
    if "miter saw" in title or "mitre saw" in title:
        return "miter-saws"
    if "circular saw" in title:
        return "circular-saws"
    if "jigsaw" in title or "jig saw" in title:
        return "jigsaws"
    if "band saw" in title:
        return "band-saws"
    if "reciprocating saw" in title or "recip saw" in title or "sawzall" in title:
        return "reciprocating-saws"

    # Drill types
    if "hammer drill" in title:
        return "hammer-drills"
    if "right angle" in title:
        return "right-angle-drills"
    if "impact driver" in title:
        return "impact-drivers"

    # Nailer types
    if "framing" in title:
        return "framing"
    if "finishing" in title or "finish nailer" in title or "brad nailer" in title:
        return "finishing"
    if "roofing" in title:
        return "roofing"
    if "flooring" in title:
        return "flooring"
    if "pneumatic" in title:
        return "pneumatic"

    # Air compressor types
    if "portable" in title or "pancake" in title:
        return "portable"
    if "stationary" in title or "vertical" in title:
        return "stationary"

    # Artificial plant types
    if "hydrangea" in title:
        return "hydrangeas"
    if "succulent" in title:
        return "succulents"
    if "tree" in title or "palm" in title or "ficus" in title:
        return "trees"
    if "flower" in title or "rose" in title or "orchid" in title:
        return "flowers"

    # Fall back to slugified subcategory if available
    if subcategory:
        return slugify(subcategory)

    return None


def compute_featured_brands(products: List[dict], max_brands: int = 6) -> List[dict]:
    """Compute featured brands from a list of products."""
    brand_counts = defaultdict(int)
    for product in products:
        brand = product.get("brand", "")
        if brand:
            brand_counts[brand] += 1

    # Sort by count descending
    sorted_brands = sorted(brand_counts.items(), key=lambda x: (-x[1], x[0]))

    featured = []
    for brand_name, count in sorted_brands[:max_brands]:
        featured.append({
            "brandId": slugify(brand_name),
            "brandName": brand_name,
            "logoUrl": f"images/brands/{slugify(brand_name)}.svg",
            "count": count
        })

    return featured


def analyze_structure():
    """Analyze the current category structure and identify issues."""
    print("=" * 60)
    print("ANALYZING CATEGORY STRUCTURE")
    print("=" * 60)

    issues = []

    for category_dir in sorted(CATEGORIES_PATH.iterdir()):
        if not category_dir.is_dir():
            continue

        category_name = category_dir.name
        print(f"\n📁 {category_name}/")

        # Find subcategory directories
        subdirs = [d for d in category_dir.iterdir() if d.is_dir()]

        for subdir in sorted(subdirs):
            subdir_name = subdir.name
            parent_json = category_dir / f"{subdir_name}.json"

            # Check if we have both directory and JSON
            if parent_json.exists():
                parent_data = load_json(parent_json)
                parent_products = parent_data.get("products", [])

                # Count products in subdirectory
                child_products = []
                for child_file in subdir.glob("*.json"):
                    child_data = load_json(child_file)
                    child_products.extend(child_data.get("products", []))

                print(f"  ├── {subdir_name}/")
                print(f"  │   ├── Parent JSON: {len(parent_products)} products")
                print(f"  │   └── Child files: {len(child_products)} products")

                if parent_products:
                    issues.append({
                        "type": "split_data",
                        "category": category_name,
                        "subcategory": subdir_name,
                        "parent_products": len(parent_products),
                        "child_products": len(child_products)
                    })

    return issues


def consolidate_category(category_name: str, subdir_name: str):
    """Consolidate a category by merging parent products into child files."""
    category_dir = CATEGORIES_PATH / category_name
    subdir = category_dir / subdir_name
    parent_json = category_dir / f"{subdir_name}.json"

    if not parent_json.exists() or not subdir.exists():
        return

    print(f"\n🔧 Consolidating {category_name}/{subdir_name}")

    parent_data = load_json(parent_json)
    parent_products = parent_data.get("products", [])

    if not parent_products:
        print("  ℹ️  No products in parent file to distribute")
        return

    # Load all child files
    child_files = {}
    for child_file in subdir.glob("*.json"):
        child_files[child_file.stem] = {
            "path": child_file,
            "data": load_json(child_file)
        }

    # Distribute parent products to appropriate child files
    distributed = 0
    unmatched = []

    for product in parent_products:
        target_slug = get_product_subcategory_slug(product)

        if target_slug and target_slug in child_files:
            # Add to existing child file
            child_files[target_slug]["data"]["products"].append(product)
            distributed += 1
        else:
            unmatched.append(product)

    print(f"  📦 Distributed {distributed} products to child files")

    if unmatched:
        print(f"  ⚠️  {len(unmatched)} products couldn't be matched to subcategory:")
        for p in unmatched[:5]:
            print(f"      - {p.get('title', 'Unknown')[:60]}...")
        if len(unmatched) > 5:
            print(f"      ... and {len(unmatched) - 5} more")

        # Create an "other" subcategory for unmatched products
        other_slug = "other"
        if other_slug not in child_files:
            other_path = subdir / f"{other_slug}.json"
            child_files[other_slug] = {
                "path": other_path,
                "data": {
                    "categoryId": f"{category_name}/{subdir_name}/{other_slug}",
                    "name": "Other",
                    "slug": other_slug,
                    "path": f"/categories/{category_name}/{subdir_name}/{other_slug}",
                    "version": "1.0",
                    "lastUpdated": datetime.now().isoformat(),
                    "breadcrumbs": [
                        {"label": "Home", "url": "/"},
                        {"label": category_name.replace("-", " ").title(), "url": f"/{category_name}"},
                        {"label": subdir_name.replace("-", " ").title(), "url": f"/{category_name}/{subdir_name}"},
                        {"label": "Other", "url": f"/{category_name}/{subdir_name}/other"}
                    ],
                    "pageInfo": {"totalResults": 0},
                    "featuredBrands": [],
                    "products": []
                }
            }

        for product in unmatched:
            child_files[other_slug]["data"]["products"].append(product)

    # Update and save all modified child files
    for slug, file_info in child_files.items():
        data = file_info["data"]
        products = data.get("products", [])

        if products:
            # Update counts and brands
            data["pageInfo"]["totalResults"] = len(products)
            data["featuredBrands"] = compute_featured_brands(products)
            data["lastUpdated"] = datetime.now().isoformat()

            save_json(file_info["path"], data)

    # Convert parent JSON to metadata-only (remove products array)
    parent_data.pop("products", None)
    parent_data["lastUpdated"] = datetime.now().isoformat()

    # Update total count to sum of all children
    total_products = sum(
        len(file_info["data"].get("products", []))
        for file_info in child_files.values()
    )
    parent_data["pageInfo"]["totalResults"] = total_products

    # Recompute featured brands from all child products
    all_products = []
    for file_info in child_files.values():
        all_products.extend(file_info["data"].get("products", []))
    parent_data["featuredBrands"] = compute_featured_brands(all_products)

    # Add subcategories reference
    parent_data["subcategories"] = [
        {
            "id": f"{category_name}/{subdir_name}/{slug}",
            "name": file_info["data"].get("name", slug.replace("-", " ").title()),
            "slug": slug,
            "productCount": len(file_info["data"].get("products", [])),
            "path": f"/categories/{category_name}/{subdir_name}/{slug}"
        }
        for slug, file_info in sorted(child_files.items())
        if file_info["data"].get("products")
    ]

    save_json(parent_json, parent_data)
    print(f"  ✅ Converted parent to metadata-only (no products array)")


def remove_duplicate_flat_files():
    """Remove flat subcategory files when nested structure exists."""
    print("\n" + "=" * 60)
    print("REMOVING DUPLICATE FLAT FILES")
    print("=" * 60)

    removed = []

    for category_dir in sorted(CATEGORIES_PATH.iterdir()):
        if not category_dir.is_dir():
            continue

        # Find subdirectories
        subdirs = {d.name for d in category_dir.iterdir() if d.is_dir()}

        # Check for flat files that are also in nested directories
        for json_file in category_dir.glob("*.json"):
            stem = json_file.stem

            # Skip if this is a parent category file (has matching directory)
            if stem in subdirs:
                continue

            # Check if this file's content is duplicated in a nested directory
            for subdir_name in subdirs:
                nested_path = category_dir / subdir_name / f"{stem}.json"
                if nested_path.exists():
                    # Compare the files
                    flat_data = load_json(json_file)
                    nested_data = load_json(nested_path)

                    flat_products = set(p.get("productId") for p in flat_data.get("products", []))
                    nested_products = set(p.get("productId") for p in nested_data.get("products", []))

                    if flat_products and nested_products:
                        overlap = flat_products & nested_products
                        if len(overlap) > 0:
                            print(f"  🗑️  Found duplicate: {category_dir.name}/{stem}.json")
                            print(f"      Also exists at: {category_dir.name}/{subdir_name}/{stem}.json")
                            print(f"      Overlap: {len(overlap)} products")
                            # Don't auto-delete, just flag
                            removed.append(json_file)

    return removed


def main():
    """Main entry point."""
    print("=" * 60)
    print("CATEGORY STRUCTURE CONSOLIDATION")
    print("=" * 60)
    print(f"Working directory: {CATEGORIES_PATH.absolute()}")

    # First, analyze the current structure
    issues = analyze_structure()

    if not issues:
        print("\n✅ No structural issues found!")
        return

    print("\n" + "=" * 60)
    print("CONSOLIDATING SPLIT DATA")
    print("=" * 60)

    # Consolidate each category with split data
    for issue in issues:
        if issue["type"] == "split_data":
            consolidate_category(issue["category"], issue["subcategory"])

    # Check for and report duplicate flat files
    duplicates = remove_duplicate_flat_files()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  📦 Consolidated {len(issues)} categories with split data")
    print(f"  ⚠️  Found {len(duplicates)} potential duplicate flat files")

    print("\n✅ Consolidation complete!")


if __name__ == "__main__":
    main()
