#!/usr/bin/env python3
"""
Integrate scraped products into the existing category structure.
Maps products to correct categories and adds them with proper structure.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from datetime import datetime

SCRAPED_DATA_PATH = Path("_scraped data/New Products")
CATEGORIES_PATH = Path("production data/categories")


def extract_product_from_manifest(manifest_path: Path) -> Optional[Dict]:
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


def extract_brand(title: str, slug: str) -> str:
    """Extract brand from product title."""
    brands = [
        'Milwaukee', 'DEWALT', 'DeWalt', 'Makita', 'RYOBI', 'Ryobi', 'Bosch', 'RIDGID', 'Ridgid',
        'Husky', 'HDX', 'Commercial Electric', 'Hampton Bay', 'Home Decorators Collection',
        'Samsung', 'LG', 'GE', 'Whirlpool', 'Frigidaire', 'KitchenAid', 'Maytag',
        'StyleWell', 'Noble House', 'Walker Edison', 'Hillsdale Furniture', 'Linon Home Decor',
        'Home Accents Holiday', 'National Tree Company', 'Nearly Natural',
        'Ring', 'Blink', 'Nest', 'Google', 'Lutron', 'Leviton', 'Square D', 'Eaton',
        'Renogy', 'Goal Zero', 'Jackery', 'EcoFlow',
        'Traeger', 'Weber', 'Char-Broil', 'Pit Boss',
        'CARRO', 'Feit Electric', 'Metalux', 'Lithonia Lighting',
        'OVIOS', 'Cambridge Casual', 'Tozey', 'Gymojoy', 'MoNiBloom', 'Uixe',
        'AURA FRAMES', 'Prepac', 'Costway', 'FUFU&GAGA', 'Techni Home', 'Coaster',
        'Mail Boss', 'Architectural Mailboxes', 'Gibraltar Mailboxes',
        'TRIXIE', 'Pawhut', 'PawHut',
        'EKIEUDL', 'Vrbgify', 'SKYSHALO', 'Busdays', 'Harper & Bright Designs',
        'Ellis Curtain', 'VECELO', 'Morden Fort', 'Signature DESIGN BY ASHLEY'
    ]

    for brand in brands:
        if brand.lower() in title.lower() or brand.lower() in slug.lower().replace('-', ' '):
            return brand

    # Try to extract first word as brand
    words = title.split()
    if words:
        return words[0]
    return "Unknown"


def categorize_product(title: str, slug: str) -> Tuple[str, Optional[str]]:
    """
    Determine category file path and subcategory based on product title/slug.
    Returns (category_file_path, subcategory)

    Maps to existing category structure in production data/categories/
    """
    title_lower = title.lower()
    slug_lower = slug.lower()
    combined = title_lower + " " + slug_lower

    # === TOOLS ===

    # Drills - impact drivers
    if 'impact driver' in combined or ('impact' in combined and 'driver' in combined):
        return ('tools/impact-drivers.json', 'impact-drivers')

    # Drills - hammer drills / rotary hammers
    if 'rotary hammer' in combined or 'hammer drill' in combined:
        return ('tools/hammer-drills.json', 'hammer-drills')

    # Drills - general
    if any(x in combined for x in ['drill', 'driver']) and 'impact' not in combined:
        if 'angle' in combined or 'right angle' in combined:
            return ('tools/right-angle-drills.json', 'right-angle-drills')
        if 'screwdriver' in combined:
            return ('tools/electric-screwdrivers.json', 'electric-screwdrivers')
        return ('tools/drills.json', 'drills')

    # Saws
    if 'miter saw' in combined:
        return ('tools/miter-saws.json', 'miter-saws')
    if 'circular saw' in combined:
        return ('tools/circular-saws.json', 'circular-saws')
    if 'table saw' in combined:
        return ('tools/table-saws.json', 'table-saws')
    if 'reciprocating saw' in combined or 'recip saw' in combined or 'sawzall' in combined:
        return ('tools/reciprocating-saws.json', 'reciprocating-saws')
    if 'jigsaw' in combined or 'jig saw' in combined:
        return ('tools/jigsaws.json', 'jigsaws')
    if 'band saw' in combined:
        return ('tools/band-saws.json', 'band-saws')
    if 'saw' in combined and not any(x in combined for x in ['sawdust', 'chain saw']):
        return ('tools/saws.json', 'saws')

    # Sanders / Polishers
    if 'sander' in combined or 'polisher' in combined or 'orbital' in combined:
        return ('tools/sanders.json', 'sanders')

    # Grinders
    if 'grinder' in combined and 'coffee' not in combined and 'meat' not in combined:
        return ('tools/grinders.json', 'grinders')

    # Nailers
    if any(x in combined for x in ['nailer', 'nail gun', 'framing nailer', 'finish nailer', 'brad nailer']):
        return ('tools/nailers.json', 'nailers')

    # Planers
    if 'planer' in combined:
        return ('tools/planers.json', 'planers')

    # Routers
    if 'router' in combined and 'wifi' not in combined and 'network' not in combined:
        return ('tools/routers.json', 'routers')

    # Air compressors
    if 'air compressor' in combined or 'compressor' in combined:
        return ('tools/air-compressors.json', 'air-compressors')

    # Batteries / Power tool batteries
    if ('battery' in combined or 'batteries' in combined) and any(x in combined for x in ['volt', 'ah', '18v', '20v', '12v', 'm12', 'm18', 'xr', 'max']):
        return ('tools/batteries.json', 'batteries')

    # Combo kits
    if 'combo kit' in combined or 'tool kit' in combined or '-tool' in combined:
        return ('tools/combo-kits.json', 'combo-kits')

    # Oscillating tools
    if 'oscillating' in combined and 'sander' not in combined:
        return ('tools/oscillating-tools.json', 'oscillating-tools')

    # === APPLIANCES ===

    # Refrigerators
    if 'refrigerator' in combined or 'fridge' in combined:
        if 'french door' in combined:
            return ('appliances/refrigerators/french-door.json', 'french-door')
        if 'side by side' in combined or 'side-by-side' in combined:
            return ('appliances/refrigerators/side-by-side.json', 'side-by-side')
        if 'top freezer' in combined:
            return ('appliances/refrigerators/top-freezer.json', 'top-freezer')
        if 'bottom freezer' in combined:
            return ('appliances/refrigerators/bottom-freezer.json', 'bottom-freezer')
        if 'mini' in combined or 'compact' in combined:
            return ('appliances/mini-fridges.json', 'mini-fridges')
        return ('appliances/refrigerators.json', 'refrigerators')

    # Washers / Dryers
    if any(x in combined for x in ['washer', 'dryer', 'laundry']):
        return ('appliances/washers-dryers.json', 'washers-dryers')

    # Dishwashers
    if 'dishwasher' in combined:
        return ('appliances/dishwashers.json', 'dishwashers')

    # Microwaves
    if 'microwave' in combined:
        return ('appliances/microwaves.json', 'microwaves')

    # Ranges / Stoves / Ovens
    if any(x in combined for x in ['range', 'stove', 'oven']) and 'range hood' not in combined:
        if 'wall oven' in combined:
            return ('appliances/wall-ovens.json', 'wall-ovens')
        return ('appliances/ranges.json', 'ranges')

    # Range hoods
    if 'range hood' in combined:
        return ('appliances/range-hoods.json', 'range-hoods')

    # Cooktops
    if 'cooktop' in combined:
        return ('appliances/cooktops.json', 'cooktops')

    # Air conditioners
    if 'air conditioner' in combined or 'ac unit' in combined:
        return ('appliances/air-conditioners.json', 'air-conditioners')

    # Fans - ceiling/tower/box
    if any(x in combined for x in ['ceiling fan', 'tower fan', 'box fan', 'fan switch', 'fan control']):
        return ('appliances/fans.json', 'fans')

    # Floor care / Vacuums
    if 'vacuum' in combined:
        return ('appliances/floor-care.json', 'floor-care')

    # === FURNITURE ===

    # Outdoor furniture - check first to avoid conflicts
    if 'patio' in combined or ('outdoor' in combined and any(x in combined for x in ['chair', 'table', 'seating', 'set', 'lounge', 'sofa', 'bench'])):
        return ('furniture/outdoor.json', 'outdoor')

    # Living room
    if any(x in combined for x in ['sofa', 'couch', 'loveseat', 'sectional', 'recliner', 'accent chair', 'arm chair', 'armchair', 'coffee table', 'end table', 'side table']):
        return ('furniture/living-room.json', 'living-room')

    # Bedroom
    if any(x in combined for x in ['bed frame', 'mattress', 'headboard', 'nightstand', 'dresser', 'bedroom']):
        return ('furniture/bedroom.json', 'bedroom')

    # Dining
    if any(x in combined for x in ['dining table', 'dining chair', 'dining set', 'bar stool', 'counter stool']):
        return ('furniture/dining.json', 'dining')

    # Office
    if any(x in combined for x in ['desk', 'office chair', 'bookcase', 'bookshelf', 'file cabinet']):
        return ('furniture/office.json', 'office')

    # Generic chair/table that didn't match above
    if 'chair' in combined or 'table' in combined:
        return ('furniture/living-room.json', 'living-room')

    # === HOME DECOR ===

    # Wall art / Digital frames
    if any(x in combined for x in ['wall art', 'canvas', 'picture frame', 'digital frame', 'digital picture']):
        return ('home-decor/wall-art.json', 'wall-art')

    # Rugs
    if 'rug' in combined or 'carpet' in combined:
        return ('home-decor/rugs.json', 'rugs')

    # Curtains / Drapes
    if 'curtain' in combined or 'drape' in combined:
        return ('home-decor/curtains.json', 'curtains')

    # Mirrors
    if 'mirror' in combined:
        return ('home-decor/mirrors.json', 'mirrors')

    # Artificial plants
    if 'artificial' in combined and any(x in combined for x in ['plant', 'tree', 'flower']):
        return ('home-decor/artificial-plants.json', 'artificial-plants')

    # Bedding
    if any(x in combined for x in ['bedding', 'comforter', 'sheet', 'pillow', 'duvet']):
        return ('home-decor/bedding.json', 'bedding')

    # === ELECTRICAL ===

    # Smart home / smart devices (but not security)
    if 'smart' in combined and any(x in combined for x in ['switch', 'dimmer', 'plug', 'outlet']):
        return ('electrical/smart-home.json', 'smart-home')

    # Light switches / dimmers (non-smart)
    if any(x in combined for x in ['light switch', 'dimmer switch', 'dimmer', 'switch']) and 'fan' not in combined:
        return ('electrical/outlets.json', 'outlets')

    # Outlets / Receptacles
    if 'outlet' in combined or 'receptacle' in combined:
        return ('electrical/outlets.json', 'outlets')

    # LED lighting / Light fixtures
    if any(x in combined for x in ['led', 'light fixture', 'strip light', 'panel light', 'high bay', 'highbay', 'skylight']):
        return ('electrical/lighting.json', 'lighting')

    # Wire / Cable
    if 'wire' in combined or 'cable' in combined:
        return ('electrical/wire-cable.json', 'wire-cable')

    # Breakers
    if 'breaker' in combined:
        return ('electrical/breakers.json', 'breakers')

    # === SMART HOME / SECURITY ===

    # Security cameras / doorbells
    if any(x in combined for x in ['security camera', 'doorbell', 'smart lock', 'camera system']):
        return ('electrical/smart-home.json', 'security')

    # === GARAGE ===

    # Garage doors
    if 'garage door' in combined:
        return ('garage/doors.json', 'doors')

    # Garage flooring
    if 'garage floor' in combined or 'floor coating' in combined:
        return ('garage/flooring.json', 'flooring')

    # === STORAGE ===

    # Shelving
    if 'shelf' in combined or 'shelving' in combined:
        return ('storage/shelving.json', 'shelving')

    # Bins / Totes
    if 'bin' in combined or 'tote' in combined or 'storage container' in combined:
        return ('storage/bins-totes.json', 'bins-totes')

    # === SOLAR / POWER ===

    # Solar panels
    if 'solar' in combined and any(x in combined for x in ['panel', 'module']):
        return ('electrical/smart-home.json', 'solar')

    # Power banks / Portable power
    if 'power bank' in combined or 'portable charger' in combined or 'power station' in combined:
        return ('electrical/smart-home.json', 'portable-power')

    # EV Chargers
    if 'ev charger' in combined or 'electric vehicle charger' in combined:
        return ('automotive.json', 'ev-chargers')

    # === AUTOMOTIVE ===
    if any(x in combined for x in ['ev charger', 'car charger', 'jump starter', 'car battery']):
        return ('automotive.json', 'automotive')

    # === OTHER / MISCELLANEOUS ===

    # Mailboxes
    if 'mailbox' in combined or 'mail box' in combined:
        return ('other.json', 'mailboxes')

    # Pet supplies
    if any(x in combined for x in ['cat tower', 'cat tree', 'dog house', 'pet']):
        return ('other.json', 'pet-supplies')

    # Default
    return ('other.json', None)


def get_existing_products() -> set:
    """Get all existing product IDs in the catalog."""
    existing = set()
    for json_file in CATEGORIES_PATH.rglob("*.json"):
        if json_file.name.startswith("_") or json_file.name == "index.json":
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


def build_product_entry(product: Dict, subcategory: Optional[str]) -> Dict:
    """Build a properly formatted product entry for the catalog."""
    brand = extract_brand(product["title"], product["slug"])

    entry = {
        "productId": product["productId"],
        "modelNumber": "",
        "brand": brand,
        "title": product["title"],
        "rating": {
            "average": 0,
            "count": 0
        },
        "images": {}
    }

    if subcategory:
        entry["subcategory"] = subcategory

    # Add images if available
    if "images" in product and product["images"]:
        imgs = product["images"]
        primary = imgs.get("primary", "")
        if primary:
            entry["images"]["primary"] = primary
            # Build size variants
            entry["images"]["thumbnail"] = re.sub(r'_\d+\.jpg$', '_100.jpg', primary)
            entry["images"]["small"] = re.sub(r'_\d+\.jpg$', '_300.jpg', primary)
            entry["images"]["medium"] = re.sub(r'_\d+\.jpg$', '_600.jpg', primary)
            entry["images"]["large"] = primary
        if imgs.get("gallery"):
            entry["images"]["gallery"] = imgs["gallery"]

    return entry


def main():
    print("=" * 60)
    print("PRODUCT INTEGRATION")
    print("=" * 60)

    # Get existing products
    print("\nLoading existing catalog...")
    existing_products = get_existing_products()
    print(f"  Found {len(existing_products)} existing products")

    # Scan scraped data
    print("\nScanning scraped products...")
    products_by_file = defaultdict(list)
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
        category_file, subcategory = categorize_product(product["title"], product["slug"])
        products_by_file[category_file].append((product, subcategory))

    print(f"\n  Total product pages scanned: {total_products}")
    print(f"  New products (not in catalog): {new_products}")
    print(f"  Skipped (not product pages): {skipped}")

    # Summary by category
    print("\n" + "=" * 60)
    print("PRODUCTS BY CATEGORY FILE")
    print("=" * 60)

    for category_file in sorted(products_by_file.keys()):
        products = products_by_file[category_file]
        print(f"\n  {category_file}: {len(products)} products")
        for p, subcat in products[:2]:
            print(f"    - [{subcat}] {p['title'][:50]}...")
        if len(products) > 2:
            print(f"    ... and {len(products) - 2} more")

    # Update category files
    print("\n" + "=" * 60)
    print("UPDATING CATEGORY FILES")
    print("=" * 60)

    updated_count = 0
    added_count = 0

    for category_file, products_list in products_by_file.items():
        file_path = CATEGORIES_PATH / category_file

        if not file_path.exists():
            print(f"\n  SKIPPING {category_file} (file doesn't exist)")
            continue

        try:
            data = json.loads(file_path.read_text())
        except:
            print(f"\n  ERROR reading {category_file}")
            continue

        # Get existing product IDs in this file
        existing_in_file = set()
        for p in data.get("products", []):
            pid = p.get("productId")
            if pid:
                existing_in_file.add(pid)

        # Add new products
        added_to_file = 0
        for product, subcategory in products_list:
            if product["productId"] not in existing_in_file:
                entry = build_product_entry(product, subcategory)
                data.setdefault("products", []).append(entry)
                added_to_file += 1
                added_count += 1

        if added_to_file > 0:
            # Update metadata
            data["lastUpdated"] = datetime.now().isoformat()
            if "pageInfo" in data:
                data["pageInfo"]["totalResults"] = len(data.get("products", []))

            # Write back
            file_path.write_text(json.dumps(data, indent=2))
            print(f"  {category_file}: +{added_to_file} products (total: {len(data.get('products', []))})")
            updated_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Files updated: {updated_count}")
    print(f"  Products added: {added_count}")
    print(f"\nDone!")


if __name__ == "__main__":
    main()
