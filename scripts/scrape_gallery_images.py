#!/usr/bin/env python3
"""
Scrape actual gallery images from Home Depot product pages.

Each product image has a unique UUID - we can't generate URLs by just changing view codes.
This script fetches the real image URLs from HD's product API/page data.
"""

import json
import re
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

CATEGORIES_PATH = Path("production data/categories")

# Headers to mimic browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def get_product_images_from_api(product_id: str) -> Optional[List[str]]:
    """
    Fetch product images using Home Depot's product API.
    """
    # HD has a product details API endpoint
    api_url = f"https://www.homedepot.com/federation-gateway/graphql?opname=productClientOnlyProduct"

    # GraphQL query for product media
    query = {
        "operationName": "productClientOnlyProduct",
        "variables": {
            "itemId": product_id,
            "storeId": "121",  # Default store
            "zipCode": "10001"
        },
        "query": """
            query productClientOnlyProduct($itemId: String!, $storeId: String, $zipCode: String) {
                product(itemId: $itemId, storeId: $storeId, zipCode: $zipCode) {
                    itemId
                    media {
                        images {
                            url
                            type
                            subType
                            sizes
                        }
                    }
                }
            }
        """
    }

    try:
        resp = requests.post(
            api_url,
            json=query,
            headers={
                **HEADERS,
                "Content-Type": "application/json",
                "x-experience-name": "general-merchandise",
            },
            timeout=15
        )

        if resp.status_code == 200:
            data = resp.json()
            product = data.get("data", {}).get("product", {})
            media = product.get("media", {})
            images = media.get("images", [])

            # Extract 600px or 1000px URLs
            urls = []
            for img in images:
                url = img.get("url", "")
                if url and "thdstatic.com" in url:
                    # Convert to 600px version
                    url_600 = re.sub(r'_\d+\.jpg$', '_600.jpg', url)
                    if url_600 not in urls:
                        urls.append(url_600)

            return urls if urls else None
    except Exception as e:
        print(f"    API error: {e}")

    return None


def get_product_images_from_page(product_id: str) -> Optional[List[str]]:
    """
    Scrape product images from the product page HTML/JSON.
    """
    url = f"https://www.homedepot.com/p/{product_id}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)

        if resp.status_code == 200:
            html = resp.text

            # Look for JSON data embedded in the page
            # HD embeds product data in script tags

            # Pattern 1: Look for mediaList in JSON
            media_pattern = r'"mediaList"\s*:\s*\[(.*?)\]'
            match = re.search(media_pattern, html, re.DOTALL)

            if match:
                try:
                    media_json = "[" + match.group(1) + "]"
                    # Clean up the JSON
                    media_json = media_json.replace("'", '"')
                    media_list = json.loads(media_json)

                    urls = []
                    for item in media_list:
                        if isinstance(item, dict):
                            url = item.get("url") or item.get("mediaUrl") or ""
                            if url and "thdstatic.com" in url:
                                url_600 = re.sub(r'_\d+\.jpg$', '_600.jpg', url)
                                if url_600 not in urls:
                                    urls.append(url_600)

                    if urls:
                        return urls
                except:
                    pass

            # Pattern 2: Look for all thdstatic image URLs
            img_pattern = r'https://images\.thdstatic\.com/productImages/[a-f0-9-]+/svn/[^"\']+_(?:100|600|1000)\.jpg'
            matches = re.findall(img_pattern, html)

            if matches:
                # Dedupe and normalize to 600px
                urls = []
                seen_uuids = set()
                for url in matches:
                    # Extract UUID
                    uuid_match = re.search(r'/productImages/([a-f0-9-]+)/', url)
                    if uuid_match:
                        uuid = uuid_match.group(1)
                        if uuid not in seen_uuids:
                            seen_uuids.add(uuid)
                            url_600 = re.sub(r'_\d+\.jpg$', '_600.jpg', url)
                            urls.append(url_600)

                if urls:
                    return urls

    except Exception as e:
        print(f"    Page scrape error: {e}")

    return None


def scrape_product_gallery(product_id: str) -> List[str]:
    """
    Get gallery images for a product, trying multiple methods.
    """
    # Try API first
    images = get_product_images_from_api(product_id)
    if images and len(images) > 1:
        return images

    # Fall back to page scraping
    images = get_product_images_from_page(product_id)
    if images:
        return images

    return []


def process_category_file(json_path: Path, limit: int = None) -> Dict:
    """
    Process a category JSON file and scrape gallery images for products.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    products = data.get("products", [])
    if not products:
        return {"path": str(json_path), "processed": 0, "updated": 0}

    processed = 0
    updated = 0

    for i, product in enumerate(products):
        if limit and processed >= limit:
            break

        product_id = product.get("productId")
        if not product_id:
            continue

        # Skip if already has gallery with multiple unique images
        existing_gallery = product.get("images", {}).get("gallery", [])
        if existing_gallery and len(existing_gallery) > 2:
            # Check if they have different UUIDs (real gallery)
            uuids = set()
            for url in existing_gallery:
                match = re.search(r'/productImages/([a-f0-9-]+)/', url)
                if match:
                    uuids.add(match.group(1))
            if len(uuids) > 2:
                continue  # Already has real gallery

        print(f"  [{i+1}/{len(products)}] Scraping {product_id}: {product.get('title', '')[:40]}...")

        gallery = scrape_product_gallery(product_id)

        if gallery:
            product.setdefault("images", {})["gallery"] = gallery
            print(f"    Found {len(gallery)} images")
            updated += 1
        else:
            print(f"    No gallery found")

        processed += 1

        # Rate limiting - be nice to HD servers
        time.sleep(0.5)

    # Save updated file
    if updated > 0:
        data["lastUpdated"] = datetime.now().isoformat()
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  Saved {json_path}")

    return {
        "path": str(json_path.relative_to(CATEGORIES_PATH.parent)),
        "processed": processed,
        "updated": updated
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scrape gallery images from Home Depot")
    parser.add_argument("--category", help="Specific category file to process (e.g., tools.json)")
    parser.add_argument("--limit", type=int, default=5, help="Max products to process per category (default: 5)")
    parser.add_argument("--product", help="Single product ID to test")
    args = parser.parse_args()

    print("=" * 60)
    print("HOME DEPOT GALLERY IMAGE SCRAPER")
    print("=" * 60)

    # Test single product
    if args.product:
        print(f"\nTesting product: {args.product}")
        gallery = scrape_product_gallery(args.product)
        if gallery:
            print(f"\nFound {len(gallery)} images:")
            for i, url in enumerate(gallery):
                print(f"  {i+1}. {url}")
        else:
            print("No gallery found")
        return

    # Process category files
    if args.category:
        json_files = [CATEGORIES_PATH / args.category]
    else:
        # Process main category files only (not subcategories)
        json_files = [
            CATEGORIES_PATH / "appliances.json",
            CATEGORIES_PATH / "tools.json",
            CATEGORIES_PATH / "furniture.json",
            CATEGORIES_PATH / "home-decor.json",
            CATEGORIES_PATH / "garage.json",
        ]

    results = []
    total_updated = 0

    for json_file in json_files:
        if not json_file.exists():
            print(f"\nSkipping {json_file} (not found)")
            continue

        print(f"\nProcessing: {json_file.name}")
        result = process_category_file(json_file, limit=args.limit)
        results.append(result)
        total_updated += result["updated"]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        print(f"  {r['path']}: {r['updated']}/{r['processed']} updated")
    print(f"\nTotal products updated: {total_updated}")


if __name__ == "__main__":
    main()
