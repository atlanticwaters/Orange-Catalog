#!/usr/bin/env python3
"""
Scrape Home Depot gallery images using Playwright.
Playwright has better bot evasion than Selenium.
"""

import json
import re
import time
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && python -m playwright install chromium")
    exit(1)

CATEGORIES_PATH = Path("production data/categories")


def scrape_product_gallery(page, product_id: str, debug: bool = False) -> List[str]:
    """
    Scrape gallery images from a product page using Playwright.
    """
    # First visit homepage to get cookies
    try:
        page.goto("https://www.homedepot.com", wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
    except:
        pass

    url = f"https://www.homedepot.com/p/{product_id}"

    try:
        page.goto(url, wait_until="domcontentloaded")

        # Wait for page content to load - longer wait
        page.wait_for_timeout(8000)

        # Get page source
        html = page.content()

        if debug:
            # Save HTML for debugging
            with open("debug_page.html", "w") as f:
                f.write(html)
            print(f"    Saved debug_page.html ({len(html)} chars)")
            print(f"    Page title: {page.title()}")

        # Check if blocked
        if "Access Denied" in html or "access denied" in html.lower():
            print("    WARNING: Access denied - bot protection triggered")
            return []

        if "Oops!! Something went wrong" in html:
            print("    WARNING: Error page - bot protection triggered")
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


def process_category_file(json_path: Path, page, limit: int = None) -> Dict:
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

        gallery = scrape_product_gallery(page, product_id)

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

    parser = argparse.ArgumentParser(description="Scrape HD gallery images with Playwright")
    parser.add_argument("--category", help="Category file (e.g., tools.json)")
    parser.add_argument("--limit", type=int, default=3, help="Max products per category")
    parser.add_argument("--product", help="Single product ID to test")
    args = parser.parse_args()

    print("=" * 60)
    print("HOME DEPOT GALLERY SCRAPER (Playwright)")
    print("=" * 60)

    # Create browser
    print("\nStarting browser...")

    with sync_playwright() as p:
        # Launch browser with stealth settings
        # Try Firefox which is less commonly fingerprinted
        browser = p.firefox.launch(
            headless=False,  # Non-headless is harder to detect
        )

        # Create context with realistic settings
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )

        # Add stealth script
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        """)

        page = context.new_page()

        try:
            # Test single product
            if args.product:
                print(f"\nTesting product: {args.product}")
                gallery = scrape_product_gallery(page, args.product, debug=True)
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
                result = process_category_file(json_file, page, limit=args.limit)
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
            browser.close()


if __name__ == "__main__":
    main()
