#!/usr/bin/env python3
"""
Manual Gallery Image Extractor

Since automated scraping is blocked by HD's bot protection, this script
provides a way to extract gallery images when you manually browse to a product page.

Usage:
1. Open a product page in Safari/Chrome manually
2. Copy the page HTML (Cmd+A, then View Source, Cmd+A, Cmd+C)
3. Run: python3 scripts/manual_gallery_extractor.py --paste
   Or save HTML to a file and run: python3 scripts/manual_gallery_extractor.py --file page.html

Alternative AppleScript method (macOS Safari):
   python3 scripts/manual_gallery_extractor.py --safari
   This will extract from the currently open Safari tab.
"""

import re
import json
import argparse
import subprocess
from pathlib import Path
from typing import List


def extract_gallery_images(html: str) -> List[str]:
    """Extract unique product gallery image URLs from page HTML."""
    # Find all thdstatic product image URLs
    img_pattern = r'https://images\.thdstatic\.com/productImages/[a-f0-9-]+/svn/[^"\'<>\s]+\.jpg'
    matches = re.findall(img_pattern, html)

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


def get_safari_html():
    """Get HTML from currently active Safari tab using AppleScript."""
    script = '''
    tell application "Safari"
        set theSource to source of document 1
        return theSource
    end tell
    '''
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"AppleScript error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error getting Safari HTML: {e}")
        return None


def get_clipboard():
    """Get content from clipboard using pbpaste."""
    try:
        result = subprocess.run(['pbpaste'], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Error getting clipboard: {e}")
        return None


def extract_product_id_from_url(html: str) -> str:
    """Try to extract product ID from the page."""
    # Look for product ID in URL patterns
    patterns = [
        r'homedepot\.com/p/[^/]+/(\d+)',
        r'"itemId"\s*:\s*"(\d+)"',
        r'"productId"\s*:\s*"(\d+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            return match.group(1)
    return "unknown"


def main():
    parser = argparse.ArgumentParser(description="Extract gallery images from HD product page")
    parser.add_argument("--file", help="HTML file to extract from")
    parser.add_argument("--paste", action="store_true", help="Extract from clipboard")
    parser.add_argument("--safari", action="store_true", help="Extract from current Safari tab")
    parser.add_argument("--output", help="Output JSON file to write gallery URLs")
    args = parser.parse_args()

    html = None

    if args.safari:
        print("Getting HTML from Safari...")
        html = get_safari_html()
    elif args.paste:
        print("Getting HTML from clipboard...")
        html = get_clipboard()
    elif args.file:
        print(f"Reading HTML from {args.file}...")
        html = Path(args.file).read_text()
    else:
        print("Please specify --safari, --paste, or --file <path>")
        print("\nUsage examples:")
        print("  python3 scripts/manual_gallery_extractor.py --safari")
        print("  python3 scripts/manual_gallery_extractor.py --paste")
        print("  python3 scripts/manual_gallery_extractor.py --file page.html")
        return

    if not html:
        print("No HTML content found")
        return

    print(f"HTML size: {len(html):,} characters")

    # Extract product ID
    product_id = extract_product_id_from_url(html)
    print(f"Product ID: {product_id}")

    # Extract gallery images
    gallery = extract_gallery_images(html)

    if gallery:
        print(f"\nFound {len(gallery)} unique gallery images:")
        print("-" * 60)
        for i, url in enumerate(gallery, 1):
            # Extract short UUID for display
            uuid = re.search(r'/productImages/([a-f0-9-]+)/', url)
            uuid_short = uuid.group(1)[:8] + "..." if uuid else "?"
            print(f"  {i}. [{uuid_short}] {url[-50:]}")

        # Output JSON
        output_data = {
            "productId": product_id,
            "gallery": gallery
        }

        if args.output:
            Path(args.output).write_text(json.dumps(output_data, indent=2))
            print(f"\nSaved to {args.output}")
        else:
            print("\n" + "-" * 60)
            print("JSON output:")
            print(json.dumps(output_data, indent=2))
    else:
        print("\nNo gallery images found in HTML")
        print("Make sure the page has fully loaded before copying HTML.")


if __name__ == "__main__":
    main()
