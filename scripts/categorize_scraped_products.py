#!/usr/bin/env python3
"""
Categorize scraped products from New Products folder.
Extracts product info and matches to existing categories.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

SCRAPED_DATA_PATH = Path("_scraped data/New Products")
CATEGORIES_PATH = Path("production data/categories")


def extract_product_from_manifest(manifest_path: Path) -> Dict:
    """Extract product info from manifest."""
    try:
        data = json.loads(manifest_path.read_text())
        original_url = data.get("originalUrl", "")
        title = data.get("title", "")

        # Check if it's a Home Depot product page
        if "homedepot.com/p/" not in original_url:
            return None

        # Extract product ID
        match = re.search(r'/p/[^/]+/(\d{9,})', original_url)
        if not match:
            return None

        product_id = match.group(1)

        # Extract product name from URL
        name_match = re.search(r'/p/([^/]+)/', original_url)
        product_slug = name_match.group(1) if name_match else ""

        # Clean up title
        clean_title = title.replace(" - The Home Depot", "").strip()

        return {
            "productId": product_id,
            "url": original_url,
            "title": clean_title,
            "slug": product_slug
        }
    except Exception as e:
        return None


def extract_images_from_html(html_path: Path) -> List[str]:
    """Extract product image URLs from HTML."""
    images = []
    try:
        html = html_path.read_text(errors='ignore')
        pattern = r'productImages/([a-f0-9-]+)/svn/([^"\'<>\s]+\.(jpg|avif|webp|png))'
        matches = re.findall(pattern, html)

        seen_uuids = set()
        for uuid, path_suffix, ext in matches:
            if uuid not in seen_uuids:
                seen_uuids.add(uuid)
                url = f"https://images.thdstatic.com/productImages/{uuid}/svn/{path_suffix}"
                # Normalize to 1000px jpg
                url = re.sub(r'_\d+\.(jpg|avif|webp|png)$', '_1000.jpg', url)
                images.append(url)
    except:
        pass
    return images


def categorize_product(title: str, slug: str) -> Tuple[str, str]:
    """
    Determine category and subcategory based on product title/slug.
    Returns (category, subcategory)
    """
    title_lower = title.lower()
    slug_lower = slug.lower()

    # Tools
    if any(x in title_lower for x in ['drill', 'driver', 'impact']):
        if 'hammer' in title_lower:
            return ('tools', 'drills/hammer-drills')
        if 'impact' in title_lower and 'driver' in title_lower:
            return ('tools', 'drills/impact-drivers')
        if 'angle' in title_lower:
            return ('tools', 'drills/angle-drills')
        return ('tools', 'drills/other')

    if any(x in title_lower for x in ['saw', 'miter', 'circular', 'table saw', 'reciprocating', 'jigsaw', 'band saw']):
        if 'miter' in title_lower:
            return ('tools', 'saws/miter-saws')
        if 'circular' in title_lower:
            return ('tools', 'saws/circular-saws')
        if 'table' in title_lower:
            return ('tools', 'saws/table-saws')
        if 'reciprocating' in title_lower:
            return ('tools', 'saws/reciprocating-saws')
        if 'jigsaw' in title_lower or 'jig saw' in title_lower:
            return ('tools', 'saws/jigsaws')
        if 'band' in title_lower:
            return ('tools', 'saws/band-saws')
        return ('tools', 'saws/other')

    if any(x in title_lower for x in ['nailer', 'nail gun', 'framing nailer', 'finish nailer', 'brad nailer', 'stapler']):
        if 'framing' in title_lower:
            return ('tools', 'nailers/framing')
        if 'finish' in title_lower:
            return ('tools', 'nailers/finishing')
        if 'roofing' in title_lower:
            return ('tools', 'nailers/roofing')
        if 'flooring' in title_lower:
            return ('tools', 'nailers/flooring')
        if 'pneumatic' in title_lower:
            return ('tools', 'nailers/pneumatic')
        return ('tools', 'nailers/other')

    if 'grinder' in title_lower:
        return ('tools', 'grinders')

    if 'sander' in title_lower:
        return ('tools', 'sanders')

    if 'planer' in title_lower:
        return ('tools', 'planers')

    if 'router' in title_lower and 'wood' in title_lower:
        return ('tools', 'routers')

    if 'air compressor' in title_lower or 'compressor' in title_lower:
        if 'portable' in title_lower:
            return ('tools', 'air-compressors/portable')
        if 'stationary' in title_lower:
            return ('tools', 'air-compressors/stationary')
        return ('tools', 'air-compressors/other')

    if 'battery' in title_lower and ('volt' in title_lower or 'ah' in title_lower):
        return ('tools', 'batteries')

    if 'combo kit' in title_lower or 'power tool kit' in title_lower:
        return ('tools', 'combo-kits')

    if 'polisher' in title_lower:
        return ('tools', 'sanders')  # Group with sanders

    if 'rotary hammer' in title_lower:
        return ('tools', 'drills/hammer-drills')

    # Appliances
    if 'refrigerator' in title_lower or 'fridge' in title_lower:
        if 'french door' in title_lower:
            return ('appliances', 'refrigerators/french-door')
        if 'side by side' in title_lower or 'side-by-side' in title_lower:
            return ('appliances', 'refrigerators/side-by-side')
        if 'top freezer' in title_lower:
            return ('appliances', 'refrigerators/top-freezer')
        if 'bottom freezer' in title_lower:
            return ('appliances', 'refrigerators/bottom-freezer')
        if 'mini' in title_lower or 'compact' in title_lower:
            return ('appliances', 'refrigerators/mini-fridges')
        return ('appliances', 'refrigerators/other')

    if 'washer' in title_lower or 'dryer' in title_lower:
        return ('appliances', 'washers-dryers')

    if 'dishwasher' in title_lower:
        return ('appliances', 'dishwashers')

    if 'microwave' in title_lower:
        return ('appliances', 'microwaves')

    if 'range' in title_lower or 'stove' in title_lower or 'oven' in title_lower:
        if 'wall oven' in title_lower:
            return ('appliances', 'wall-ovens')
        return ('appliances', 'ranges')

    if 'cooktop' in title_lower:
        return ('appliances', 'cooktops')

    if 'air conditioner' in title_lower or 'ac unit' in title_lower:
        return ('appliances', 'air-conditioners')

    if 'fan' in title_lower and ('ceiling' in title_lower or 'tower' in title_lower or 'box' in title_lower):
        return ('appliances', 'fans')

    if 'vacuum' in title_lower:
        return ('appliances', 'floor-care')

    # Furniture
    if any(x in title_lower for x in ['sofa', 'couch', 'loveseat', 'sectional', 'recliner']):
        return ('furniture', 'living-room')

    if any(x in title_lower for x in ['bed frame', 'mattress', 'headboard', 'nightstand', 'dresser', 'bedroom']):
        return ('furniture', 'bedroom')

    if any(x in title_lower for x in ['dining table', 'dining chair', 'dining set']):
        return ('furniture', 'dining')

    if any(x in title_lower for x in ['desk', 'office chair', 'bookcase', 'bookshelf']):
        return ('furniture', 'office')

    if 'patio' in title_lower or 'outdoor' in title_lower:
        if 'chair' in title_lower or 'lounge' in title_lower or 'seating' in title_lower:
            return ('furniture', 'outdoor')
        if 'table' in title_lower:
            return ('furniture', 'outdoor')
        if 'set' in title_lower:
            return ('furniture', 'outdoor')

    if 'chair' in title_lower or 'arm chair' in title_lower:
        return ('furniture', 'living-room')

    if 'table' in title_lower and 'accent' in title_lower:
        return ('furniture', 'living-room')

    if 'coffee table' in title_lower:
        return ('furniture', 'living-room')

    # Home Decor
    if 'rug' in title_lower or 'carpet' in title_lower:
        return ('home-decor', 'rugs')

    if 'curtain' in title_lower or 'drape' in title_lower:
        return ('home-decor', 'curtains')

    if 'mirror' in title_lower:
        return ('home-decor', 'mirrors')

    if 'wall art' in title_lower or 'canvas' in title_lower or 'picture frame' in title_lower or 'digital frame' in title_lower:
        return ('home-decor', 'wall-art')

    if 'bedding' in title_lower or 'comforter' in title_lower or 'sheet' in title_lower or 'pillow' in title_lower:
        return ('home-decor', 'bedding')

    if 'artificial' in title_lower and ('plant' in title_lower or 'tree' in title_lower or 'flower' in title_lower):
        return ('home-decor', 'artificial-plants/other')

    # Electrical
    if 'switch' in title_lower and ('light' in title_lower or 'smart' in title_lower or 'dimmer' in title_lower):
        return ('electrical', 'outlets')

    if 'outlet' in title_lower or 'receptacle' in title_lower:
        return ('electrical', 'outlets')

    if 'led' in title_lower and ('light' in title_lower or 'strip' in title_lower or 'fixture' in title_lower):
        return ('electrical', 'lighting')

    if 'wire' in title_lower or 'cable' in title_lower:
        return ('electrical', 'wire-cable')

    if 'breaker' in title_lower:
        return ('electrical', 'breakers')

    # Garage
    if 'garage door' in title_lower:
        return ('garage', 'doors')

    if 'floor coating' in title_lower or 'garage floor' in title_lower:
        return ('garage', 'flooring')

    # Storage
    if 'shelf' in title_lower or 'shelving' in title_lower:
        return ('storage', 'shelving')

    if 'bin' in title_lower or 'tote' in title_lower or 'storage container' in title_lower:
        return ('storage', 'bins-totes')

    # Smart Home / Security
    if 'security camera' in title_lower or 'doorbell' in title_lower or 'smart lock' in title_lower:
        return ('smart-home', 'security')

    if 'smart' in title_lower and ('speaker' in title_lower or 'display' in title_lower):
        return ('smart-home', 'speakers')

    # Solar / Power
    if 'solar' in title_lower and ('panel' in title_lower or 'battery' in title_lower or 'charger' in title_lower):
        return ('solar', 'panels')

    if 'power bank' in title_lower or 'portable charger' in title_lower:
        return ('solar', 'batteries')

    # Default
    return ('other', None)


def get_existing_products() -> set:
    """Get all existing product IDs in the catalog."""
    existing = set()
    for json_file in CATEGORIES_PATH.rglob("*.json"):
        if json_file.name.startswith("_"):
            continue
        try:
            data = json.loads(json_file.read_text())
            for product in data.get("products", []):
                pid = product.get("productId")
                if pid:
                    existing.add(pid)
        except:
            pass
    return existing


def main():
    print("=" * 60)
    print("PRODUCT CATEGORIZER")
    print("=" * 60)

    # Get existing products
    print("\nLoading existing catalog...")
    existing_products = get_existing_products()
    print(f"  Found {len(existing_products)} existing products")

    # Scan scraped data
    print("\nScanning scraped products...")
    products_by_category = defaultdict(list)
    total_products = 0
    new_products = 0
    skipped = 0

    for folder in SCRAPED_DATA_PATH.iterdir():
        if not folder.is_dir():
            continue

        manifest_path = folder / "manifest.json"
        index_path = folder / "index.html"

        if not manifest_path.exists():
            continue

        product = extract_product_from_manifest(manifest_path)
        if not product:
            skipped += 1
            continue

        total_products += 1

        # Skip if already in catalog
        if product["productId"] in existing_products:
            continue

        new_products += 1

        # Get images
        if index_path.exists():
            images = extract_images_from_html(index_path)
            if images:
                product["images"] = {
                    "primary": images[0],
                    "gallery": images if len(images) > 1 else []
                }

        # Categorize
        category, subcategory = categorize_product(product["title"], product["slug"])
        key = f"{category}/{subcategory}" if subcategory else category
        products_by_category[key].append(product)

    print(f"\n  Total product pages scanned: {total_products}")
    print(f"  New products (not in catalog): {new_products}")
    print(f"  Skipped (not product pages): {skipped}")

    # Summary by category
    print("\n" + "=" * 60)
    print("PRODUCTS BY CATEGORY")
    print("=" * 60)

    for category in sorted(products_by_category.keys()):
        products = products_by_category[category]
        print(f"\n  {category}: {len(products)} products")
        for p in products[:3]:
            print(f"    - {p['title'][:60]}...")
        if len(products) > 3:
            print(f"    ... and {len(products) - 3} more")

    # Output JSON for each category
    print("\n" + "=" * 60)
    print("OUTPUTTING CATEGORY FILES")
    print("=" * 60)

    output_path = Path("_scraped data/categorized_products")
    output_path.mkdir(exist_ok=True)

    for category_path, products in products_by_category.items():
        # Create safe filename
        filename = category_path.replace("/", "_") + ".json"
        filepath = output_path / filename

        output_data = {
            "category": category_path,
            "count": len(products),
            "products": products
        }

        filepath.write_text(json.dumps(output_data, indent=2))
        print(f"  Wrote {filename}: {len(products)} products")

    print(f"\nDone! Output files in: {output_path}")


if __name__ == "__main__":
    main()
