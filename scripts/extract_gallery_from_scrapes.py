#!/usr/bin/env python3
"""
Extract gallery images from scraped THD pages.

Parses the manifest.json and index.html files to extract product image URLs
and maps them to product IDs in our catalog.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


SCRAPED_DATA_PATH = Path("_scraped data/THD Product Page Data")
CATEGORIES_PATH = Path("production data/categories")
PRODUCTS_PATH = Path("production data/products")


def extract_product_ids_from_html(html_path: Path) -> List[str]:
    """Extract product IDs from an HTML file."""
    try:
        html = html_path.read_text(errors='ignore')
        # Match product URLs like /p/Product-Name/123456789
        pattern = r'homedepot\.com/p/[^/]+/(\d{9,})'
        matches = re.findall(pattern, html)
        return list(set(matches))  # Dedupe
    except Exception as e:
        print(f"  Error reading {html_path}: {e}")
        return []


def extract_product_id_from_manifest(manifest_path: Path) -> str:
    """Extract product ID from manifest's originalUrl if it's a PDP."""
    try:
        data = json.loads(manifest_path.read_text())
        original_url = data.get("originalUrl", "")
        # Match /p/Product-Name/123456789
        match = re.search(r'/p/[^/]+/(\d{9,})', original_url)
        return match.group(1) if match else None
    except:
        return None


def extract_images_from_html(html_path: Path) -> Dict[str, str]:
    """
    Extract product images from HTML file.
    Returns dict mapping UUID to normalized image URL.
    """
    uuid_images = {}
    try:
        html = html_path.read_text(errors='ignore')
        # Find all productImages URLs in HTML
        pattern = r'productImages/([a-f0-9-]+)/svn/([^"\'<>\s]+\.(jpg|avif|webp|png))'
        matches = re.findall(pattern, html)

        for uuid, path_suffix, ext in matches:
            # Build full URL and normalize to 1000px jpg
            base_url = f"https://images.thdstatic.com/productImages/{uuid}/svn/{path_suffix}"
            # Normalize to 1000px
            normalized = re.sub(r'_\d+\.(jpg|avif|webp|png)$', '_1000.jpg', base_url)
            uuid_images[uuid] = normalized

    except Exception as e:
        pass  # Silently skip errors

    return uuid_images


def extract_images_from_manifest(manifest_path: Path) -> Dict[str, List[str]]:
    """
    Extract product images from manifest.json.
    Returns dict mapping UUID to list of image URLs.
    """
    try:
        data = json.loads(manifest_path.read_text())
        resources = data.get("resources", {})

        # Extract productImages URLs and group by UUID
        uuid_images = defaultdict(list)

        for local_file, original_url in resources.items():
            if "productImages" in original_url and "/svn/" in original_url:
                # Extract UUID from URL
                uuid_match = re.search(r'/productImages/([a-f0-9-]+)/', original_url)
                if uuid_match:
                    uuid = uuid_match.group(1)
                    # Normalize to 1000px (largest size)
                    normalized_url = re.sub(r'_\d+\.jpg$', '_1000.jpg', original_url)
                    normalized_url = re.sub(r'_\d+\.avif$', '_1000.jpg', original_url)
                    # Replace avif/webp extension with jpg
                    normalized_url = re.sub(r'\.(avif|webp)$', '.jpg', normalized_url)
                    uuid_images[uuid].append(normalized_url)

        return dict(uuid_images)

    except Exception as e:
        print(f"  Error reading {manifest_path}: {e}")
        return {}


def get_catalog_products() -> Dict[str, dict]:
    """Load all products from our catalog."""
    products = {}

    # Load from category files
    for json_file in CATEGORIES_PATH.rglob("*.json"):
        if json_file.name.startswith("_") or json_file.name == "index.json":
            continue
        try:
            data = json.loads(json_file.read_text())
            for product in data.get("products", []):
                pid = product.get("productId")
                if pid:
                    products[pid] = {
                        "product": product,
                        "file": json_file,
                        "primary_uuid": None
                    }
                    # Extract UUID from primary image
                    primary = product.get("images", {}).get("primary", "")
                    if primary:
                        match = re.search(r'/productImages/([a-f0-9-]+)/', primary)
                        if match:
                            products[pid]["primary_uuid"] = match.group(1)
        except Exception as e:
            print(f"  Error loading {json_file}: {e}")

    return products


def find_gallery_for_product(product_id: str, primary_uuid: str, scraped_images: Dict[str, List[str]]) -> List[str]:
    """Find gallery images for a product based on its primary UUID."""
    gallery = []

    # First, check if we have images with the same UUID
    if primary_uuid and primary_uuid in scraped_images:
        for url in scraped_images[primary_uuid]:
            if url not in gallery:
                gallery.append(url)

    # Also look for images in the same product slug
    # (Images may have different UUIDs but same product name pattern)

    return gallery


def scan_scraped_folders() -> Dict[str, Dict]:
    """
    Scan all scraped folders and build a mapping of:
    - product_id -> list of gallery image URLs
    """
    product_galleries = defaultdict(set)
    all_scraped_images = {}
    pdp_count = 0
    plp_count = 0

    # Folders to scan
    folders_to_scan = [
        SCRAPED_DATA_PATH / "_New Stuff",
        SCRAPED_DATA_PATH / "Tool Categories",
        SCRAPED_DATA_PATH / "PLP Landing Pages",
        SCRAPED_DATA_PATH / "Fridge PLP",
        SCRAPED_DATA_PATH / "Top Level THD Pages",
        Path("_scraped data/New Products"),  # New folder with 1126 products
    ]

    for base_folder in folders_to_scan:
        if not base_folder.exists():
            continue

        print(f"\nScanning: {base_folder.name}")

        for folder in base_folder.iterdir():
            if not folder.is_dir():
                continue

            manifest_path = folder / "manifest.json"
            index_path = folder / "index.html"

            if not manifest_path.exists() or not index_path.exists():
                continue

            # Check if this is a PDP (single product page)
            pdp_product_id = extract_product_id_from_manifest(manifest_path)

            # Extract images from HTML (more complete than manifest)
            html_images = extract_images_from_html(index_path)

            if not html_images:
                # Fall back to manifest
                uuid_images = extract_images_from_manifest(manifest_path)
                if uuid_images:
                    for uuid, urls in uuid_images.items():
                        if urls:
                            html_images[uuid] = urls[0]

            if not html_images:
                continue

            # Store all images for UUID matching
            all_scraped_images.update(html_images)

            if pdp_product_id:
                # This is a PDP - all images belong to this one product
                pdp_count += 1
                for uuid, url in html_images.items():
                    product_galleries[pdp_product_id].add(url)
            else:
                # This is a PLP - get product IDs from HTML
                plp_count += 1
                product_ids = extract_product_ids_from_html(index_path)

                # Add all images to all products on the page
                for pid in product_ids:
                    for uuid, url in html_images.items():
                        product_galleries[pid].add(url)

    print(f"\n  PDPs processed: {pdp_count}")
    print(f"  PLPs processed: {plp_count}")

    return {
        "product_galleries": {k: list(v) for k, v in product_galleries.items()},
        "all_images": all_scraped_images
    }


def main():
    print("=" * 60)
    print("GALLERY IMAGE EXTRACTOR")
    print("=" * 60)

    # Load our catalog
    print("\nLoading catalog products...")
    catalog = get_catalog_products()
    print(f"  Found {len(catalog)} products in catalog")

    # Scan scraped data
    print("\nScanning scraped data...")
    scraped = scan_scraped_folders()
    product_galleries = scraped["product_galleries"]
    all_images = scraped["all_images"]

    print(f"\n  Found {len(product_galleries)} products with gallery images")
    print(f"  Found {len(all_images)} unique image UUIDs")

    # Match and update products
    print("\n" + "=" * 60)
    print("MATCHING PRODUCTS")
    print("=" * 60)

    matched = 0
    updated_files = set()

    for pid, data in catalog.items():
        primary_uuid = data["primary_uuid"]

        # Check if we have direct gallery from scrape
        if pid in product_galleries:
            gallery = product_galleries[pid]
        # Or match by UUID
        elif primary_uuid and primary_uuid in all_images:
            gallery = all_images[primary_uuid]
        else:
            continue

        # Filter to unique UUIDs and normalize
        unique_gallery = []
        seen_uuids = set()
        for url in gallery:
            uuid_match = re.search(r'/productImages/([a-f0-9-]+)/', url)
            if uuid_match:
                uuid = uuid_match.group(1)
                if uuid not in seen_uuids:
                    seen_uuids.add(uuid)
                    # Normalize URL to 1000px
                    normalized = re.sub(r'_\d+\.jpg$', '_1000.jpg', url)
                    normalized = re.sub(r'\.(avif|webp)$', '.jpg', normalized)
                    unique_gallery.append(normalized)

        # Only accept reasonable gallery sizes (2-20 images)
        # More than 20 is likely a bug in matching
        if len(unique_gallery) >= 2 and len(unique_gallery) <= 20:
            print(f"\n  {pid}: {len(unique_gallery)} gallery images")
            matched += 1
            updated_files.add(data["file"])

            # Update the product in the file
            # Store for batch update
            data["new_gallery"] = unique_gallery

    print(f"\n\nMatched {matched} products with gallery images")
    print(f"Files to update: {len(updated_files)}")

    # Now update the files
    if matched > 0:
        print("\n" + "=" * 60)
        print("UPDATING FILES")
        print("=" * 60)

        for json_file in updated_files:
            data = json.loads(json_file.read_text())
            updated = 0

            for product in data.get("products", []):
                pid = product.get("productId")
                if pid and pid in catalog and "new_gallery" in catalog[pid]:
                    product.setdefault("images", {})["gallery"] = catalog[pid]["new_gallery"]
                    updated += 1

            if updated > 0:
                json_file.write_text(json.dumps(data, indent=2))
                print(f"  Updated {json_file.name}: {updated} products")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Catalog products: {len(catalog)}")
    print(f"  Products with scraped galleries: {len(product_galleries)}")
    print(f"  Products matched & updated: {matched}")


if __name__ == "__main__":
    main()
