#!/usr/bin/env python3
"""
Scrape Home Depot gallery images using Selenium with Safari.
This bypasses bot protection by using a real browser.
"""

import json
import re
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Dependencies not installed. Run: pip install undetected-chromedriver selenium")
    exit(1)

CATEGORIES_PATH = Path("production data/categories")


def create_driver():
    """Create undetected Chrome webdriver."""
    options = uc.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Use undetected-chromedriver which patches Chrome to avoid detection
    driver = uc.Chrome(options=options, headless=True)
    driver.set_page_load_timeout(30)

    return driver


def scrape_product_gallery(driver, product_id: str, debug: bool = False) -> List[str]:
    """
    Scrape gallery images from a product page using Selenium.
    """
    url = f"https://www.homedepot.com/p/{product_id}"

    try:
        driver.get(url)

        # Wait for page to load
        time.sleep(5)

        # Get page source
        html = driver.page_source

        if debug:
            # Save HTML for debugging
            with open("debug_page.html", "w") as f:
                f.write(html)
            print(f"    Saved debug_page.html ({len(html)} chars)")
            print(f"    Page title: {driver.title}")

        # Check if blocked
        if "Access Denied" in html or "access denied" in html.lower():
            print("    WARNING: Access denied - bot protection triggered")
            return []

        # Find all image URLs
        img_pattern = r'https://images\.thdstatic\.com/productImages/[a-f0-9-]+/svn/[^"\'<>\s]+\.jpg'
        matches = re.findall(img_pattern, html)

        if debug:
            print(f"    Found {len(matches)} raw image URL matches")

        # Dedupe by UUID and normalize to 600px
        uuids = {}
        for img_url in matches:
            uuid_match = re.search(r'/productImages/([a-f0-9-]+)/', img_url)
            if uuid_match:
                uuid = uuid_match.group(1)
                if uuid not in uuids:
                    # Normalize to 600px
                    url_600 = re.sub(r'_\d+\.jpg$', '_600.jpg', img_url)
                    uuids[uuid] = url_600

        return list(uuids.values())

    except Exception as e:
        print(f"    Error: {e}")
        return []


def process_category_file(json_path: Path, driver, limit: int = None) -> Dict:
    """
    Process a category JSON file and scrape gallery images.
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

        # Skip if already has real gallery (multiple UUIDs)
        existing_gallery = product.get("images", {}).get("gallery", [])
        if existing_gallery and len(existing_gallery) > 2:
            uuids = set()
            for url in existing_gallery:
                match = re.search(r'/productImages/([a-f0-9-]+)/', url)
                if match:
                    uuids.add(match.group(1))
            if len(uuids) > 2:
                continue

        print(f"  [{i+1}/{len(products)}] Scraping {product_id}: {product.get('title', '')[:40]}...")

        gallery = scrape_product_gallery(driver, product_id)

        if gallery and len(gallery) > 1:
            product.setdefault("images", {})["gallery"] = gallery
            print(f"    Found {len(gallery)} unique images")
            updated += 1
        else:
            print(f"    No gallery found (got {len(gallery)} images)")

        processed += 1

        # Small delay between requests
        time.sleep(1)

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

    parser = argparse.ArgumentParser(description="Scrape HD gallery images with Safari")
    parser.add_argument("--category", help="Category file (e.g., tools.json)")
    parser.add_argument("--limit", type=int, default=3, help="Max products per category")
    parser.add_argument("--product", help="Single product ID to test")
    args = parser.parse_args()

    print("=" * 60)
    print("HOME DEPOT GALLERY SCRAPER (Safari)")
    print("=" * 60)

    # Create browser
    print("\nStarting Safari browser...")
    driver = create_driver()

    try:
        # Test single product
        if args.product:
            print(f"\nTesting product: {args.product}")
            gallery = scrape_product_gallery(driver, args.product, debug=True)
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
            json_files = [
                CATEGORIES_PATH / "appliances.json",
                CATEGORIES_PATH / "tools.json",
            ]

        results = []
        total_updated = 0

        for json_file in json_files:
            if not json_file.exists():
                print(f"\nSkipping {json_file} (not found)")
                continue

            print(f"\nProcessing: {json_file.name}")
            result = process_category_file(json_file, driver, limit=args.limit)
            results.append(result)
            total_updated += result["updated"]

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        for r in results:
            print(f"  {r['path']}: {r['updated']}/{r['processed']} updated")
        print(f"\nTotal: {total_updated}")

    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
