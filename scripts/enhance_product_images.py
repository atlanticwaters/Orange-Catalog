#!/usr/bin/env python3
"""
Enhance product images by generating multiple image URLs.

Home Depot image URL pattern:
https://images.thdstatic.com/productImages/{uuid}/svn/{product-slug}-{view_code}_{size}.jpg

View codes represent different product angles/views:
- 64: Primary/hero image
- 1d, 1f, 4f: Front views, doors closed
- 31, 40, 44: Interior views
- 66, 76: Side/angle views
- a0, c3, d4, fa: Detail/feature shots

Available sizes:
- 100: Thumbnail (100px)
- 300: Small (300px) - not always available
- 600: Medium (600px) - good balance of quality/size
- 1000: Large (1000px)

This script:
1. Takes existing primary image URL (typically 64_100.jpg)
2. Generates 600px URLs for the primary and common alternate views
3. Updates product data structure with gallery array
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

CATEGORIES_PATH = Path("production data/categories")

# Common view codes for product images (in order of importance)
# 64 is always the primary/hero image
VIEW_CODES = ["64", "1d", "1f", "4f", "31", "40", "44", "66", "76", "a0", "c3", "d4", "fa"]

# Standard size for gallery images (good balance of quality and bandwidth)
GALLERY_SIZE = "600"


def load_json(path: Path) -> dict:
    """Load a JSON file."""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """Save data to a JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def extract_image_base(image_url: str) -> Optional[Dict[str, str]]:
    """
    Extract the base URL components from a Home Depot image URL.

    Example:
    Input:  https://images.thdstatic.com/productImages/xxx/svn/product-name-64_100.jpg
    Output: {
        "base": "https://images.thdstatic.com/productImages/xxx/svn/product-name",
        "extension": ".jpg"
    }
    """
    if not image_url or "thdstatic.com" not in image_url:
        return None

    # Match the view code and size suffix pattern (e.g., -64_100, -1d_600, etc.)
    # View codes can be: 64, 1d, 1f, 4f, 31, 40, 44, 66, 76, a0, c3, d4, fa
    pattern = r'(.*)-([0-9a-f]{2})_\d+(\.\w+)$'
    match = re.match(pattern, image_url)

    if match:
        return {
            "base": match.group(1),
            "extension": match.group(3)
        }

    return None


def generate_gallery_urls(primary_url: str) -> List[str]:
    """
    Generate 600px URLs for all common product views.

    Returns a list of URLs for different product angles/views.
    The first URL is always the primary (64) image.
    """
    components = extract_image_base(primary_url)

    if not components:
        # Can't parse the URL, return just the primary
        return [primary_url]

    base = components["base"]
    ext = components["extension"]

    # Generate URLs for all view codes at 600px
    gallery = []
    for view_code in VIEW_CODES:
        gallery.append(f"{base}-{view_code}_{GALLERY_SIZE}{ext}")

    return gallery


def generate_image_variants(primary_url: str) -> Dict[str, str]:
    """
    Generate size variants for the primary image only.

    Returns a dict with size names as keys and URLs as values.
    """
    components = extract_image_base(primary_url)

    if not components:
        return {"primary": primary_url}

    base = components["base"]
    ext = components["extension"]

    return {
        "primary": primary_url,
        "thumbnail": f"{base}-64_100{ext}",
        "small": f"{base}-64_300{ext}",
        "medium": f"{base}-64_600{ext}",
        "large": f"{base}-64_1000{ext}"
    }


def enhance_product_images(product: dict) -> dict:
    """
    Enhance a single product's image data.

    Transforms:
    {
        "images": {
            "primary": "https://...64_100.jpg"
        }
    }

    Into:
    {
        "images": {
            "primary": "https://...64_100.jpg",
            "thumbnail": "https://...64_100.jpg",
            "small": "https://...64_300.jpg",
            "medium": "https://...64_600.jpg",
            "large": "https://...64_1000.jpg",
            "gallery": [
                "https://...64_600.jpg",
                "https://...1d_600.jpg",
                "https://...1f_600.jpg",
                ...
            ]
        }
    }
    """
    images = product.get("images", {})
    primary_url = images.get("primary", "")

    if not primary_url:
        return product

    # Generate size variants for primary image
    variants = generate_image_variants(primary_url)

    # Generate gallery URLs for all views at 600px
    gallery = generate_gallery_urls(primary_url)

    # Build new images object
    new_images = variants.copy()
    new_images["gallery"] = gallery

    product["images"] = new_images
    return product


def process_json_file(json_path: Path) -> dict:
    """Process a single JSON file and enhance all product images."""
    data = load_json(json_path)
    products = data.get("products", [])

    if not products:
        return {"path": str(json_path), "enhanced": 0, "skipped": 0}

    enhanced = 0
    skipped = 0

    for product in products:
        primary_url = product.get("images", {}).get("primary", "")

        if primary_url and "thdstatic.com" in primary_url:
            enhance_product_images(product)
            enhanced += 1
        else:
            skipped += 1

    # Update timestamp
    data["lastUpdated"] = datetime.now().isoformat()

    # Save the enhanced file
    save_json(json_path, data)

    return {
        "path": str(json_path.relative_to(CATEGORIES_PATH)),
        "enhanced": enhanced,
        "skipped": skipped
    }


def main():
    """Enhance images for all products in all category files."""
    print("=" * 60)
    print("ENHANCING PRODUCT IMAGES")
    print("=" * 60)
    print(f"\nGenerating gallery with {len(VIEW_CODES)} view angles at {GALLERY_SIZE}px:")
    print(f"  View codes: {', '.join(VIEW_CODES)}")

    results = []
    total_enhanced = 0
    total_skipped = 0

    # Process all JSON files in categories directory
    print("\n📁 Processing category files...")

    for json_file in sorted(CATEGORIES_PATH.rglob("*.json")):
        # Skip index.json
        if json_file.name == "index.json":
            continue

        # Skip _all.json files (they'll be regenerated)
        if json_file.name.startswith("_"):
            continue

        result = process_json_file(json_file)

        if result["enhanced"] > 0 or result["skipped"] > 0:
            print(f"  ✅ {result['path']}: {result['enhanced']} enhanced, {result['skipped']} skipped")
            results.append(result)
            total_enhanced += result["enhanced"]
            total_skipped += result["skipped"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  📦 Files processed: {len(results)}")
    print(f"  🖼️  Products enhanced: {total_enhanced}")
    print(f"  ⚠️  Products skipped: {total_skipped}")

    print("\n" + "=" * 60)
    print("📱 iOS APP USAGE")
    print("=" * 60)
    print("""
Products now have multiple image sizes AND a gallery array:

{
  "images": {
    "primary": "https://...64_100.jpg",   // Original (backward compatible)
    "thumbnail": "https://...64_100.jpg", // 100px - for lists
    "small": "https://...64_300.jpg",     // 300px - for grids
    "medium": "https://...64_600.jpg",    // 600px - for detail views
    "large": "https://...64_1000.jpg",    // 1000px - for zoom
    "gallery": [                          // All views at 600px
      "https://...64_600.jpg",            // Primary view
      "https://...1d_600.jpg",            // Alternate angle
      "https://...1f_600.jpg",            // Interior view
      "https://...4f_600.jpg",            // Detail shot
      ...                                 // Up to 13 different views
    ]
  }
}

Usage in iOS:
- Use 'thumbnail' for UITableView cells
- Use 'small' for UICollectionView grids
- Use 'medium' for product detail hero image
- Use 'large' for pinch-to-zoom on hero
- Use 'gallery' array for product image carousel/slider
  - Load lazily, not all views exist for every product
  - Handle 404s gracefully (some view codes don't exist)

Note: Run generate_all_products.py after this to update _all.json files!
""")


if __name__ == "__main__":
    main()
