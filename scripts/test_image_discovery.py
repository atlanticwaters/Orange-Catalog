#!/usr/bin/env python3
"""
Test discovering product gallery images by checking the CDN directly.

Since each gallery image has a unique UUID, we can't generate them.
But maybe we can find patterns or probe the CDN.
"""

import requests
import re
import json
from pathlib import Path

# Test with known working image URLs the user provided
TEST_IMAGES = [
    "https://images.thdstatic.com/productImages/0674b531-2a4d-4408-8486-15feed80b1d2/svn/stainless-steel-ge-french-door-refrigerators-gne27jymfs-44_1000.jpg",
    "https://images.thdstatic.com/productImages/2b401aec-6a63-4509-9069-1261b321bc3d/svn/stainless-steel-ge-french-door-refrigerators-gne27jymfs-64_1000.jpg",
    "https://images.thdstatic.com/productImages/d02600db-4ab8-46aa-9fd1-886ed61916b7/svn/stainless-steel-ge-french-door-refrigerators-gne27jymfs-40_1000.jpg",
]

def test_image_accessibility():
    """Test if we can access images directly from CDN."""
    print("Testing direct image access from CDN...")
    print("=" * 60)

    for url in TEST_IMAGES:
        # Extract UUID
        uuid_match = re.search(r'/productImages/([a-f0-9-]+)/', url)
        uuid = uuid_match.group(1) if uuid_match else "unknown"

        try:
            resp = requests.head(url, timeout=10)
            print(f"\nUUID: {uuid[:20]}...")
            print(f"  Status: {resp.status_code}")
            print(f"  Content-Type: {resp.headers.get('content-type', 'N/A')}")
            print(f"  Content-Length: {resp.headers.get('content-length', 'N/A')}")
        except Exception as e:
            print(f"\nUUID: {uuid[:20]}...")
            print(f"  Error: {e}")


def test_google_search_api():
    """
    Test using Google Custom Search to find product images.
    This would require API keys, just showing the concept.
    """
    print("\nAlternative approach: Use site-specific Google search")
    print("=" * 60)
    print("""
    You could use Google Custom Search API:
    - Search: site:images.thdstatic.com productImages GNE27JYMFS
    - This would return indexed image URLs

    Or use DuckDuckGo (no API key needed):
    - Search: site:homedepot.com GNE27JYMFS images
    """)


def check_existing_products():
    """Check what products we have and their current image data."""
    print("\nChecking existing product data...")
    print("=" * 60)

    categories_path = Path("production data/categories")

    for json_file in sorted(categories_path.glob("*.json"))[:2]:
        if json_file.name.startswith("_") or json_file.name == "index.json":
            continue

        with open(json_file) as f:
            data = json.load(f)

        products = data.get("products", [])[:3]

        print(f"\n{json_file.name}:")
        for p in products:
            pid = p.get("productId", "N/A")
            title = p.get("title", "N/A")[:40]
            primary = p.get("images", {}).get("primary", "")

            # Extract UUID from primary image
            uuid = "N/A"
            if primary:
                match = re.search(r'/productImages/([a-f0-9-]+)/', primary)
                if match:
                    uuid = match.group(1)[:20] + "..."

            print(f"  {pid}: {title}")
            print(f"    Primary UUID: {uuid}")


if __name__ == "__main__":
    test_image_accessibility()
    check_existing_products()
    test_google_search_api()
