#!/usr/bin/env python3
"""
Extract complete product data from saved HTML files
Parses JSON-LD structured data to get full product details
"""

import json
import re
from pathlib import Path
from datetime import datetime


def extract_product_data_from_html(html_content: str) -> list:
    """Extract product data from JSON-LD structured data in HTML"""
    products = []
    
    # Find all script tags with JSON-LD
    script_pattern = r'<script[^>]*type=["\']?application/ld\+json["\']?[^>]*>(.*?)</script>'
    matches = re.findall(script_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        try:
            data = json.loads(match)
            
            # Handle array wrapper
            if isinstance(data, list):
                for item in data:
                    products.extend(_extract_products_from_item(item))
            else:
                products.extend(_extract_products_from_item(data))
                
        except json.JSONDecodeError:
            continue
    
    return products


def _extract_products_from_item(item: dict) -> list:
    """Extract products from a JSON-LD item"""
    products = []
    
    if not isinstance(item, dict):
        return products
    
    # Check if this is a WebPage with product offers
    if item.get('@type') == 'WebPage':
        main_entity = item.get('mainEntity', {})
        if isinstance(main_entity, dict):
            offers = main_entity.get('offers', {})
            if isinstance(offers, dict):
                items_offered = offers.get('itemOffered', [])
                if isinstance(items_offered, list):
                    for product in items_offered:
                        if isinstance(product, dict) and product.get('@type') == 'Product':
                            products.append(_normalize_product(product))
    
    # Check if this is directly a Product
    elif item.get('@type') == 'Product':
        products.append(_normalize_product(item))
    
    return products


def _normalize_product(product: dict) -> dict:
    """Normalize product data to consistent format"""
    # Extract rating info
    rating_data = product.get('aggregateRating', {})
    if isinstance(rating_data, dict):
        rating = {
            'average': float(rating_data.get('ratingValue', 0)),
            'count': int(rating_data.get('reviewCount', 0)),
            'best': int(rating_data.get('bestRating', 5)),
            'worst': int(rating_data.get('worstRating', 1))
        }
    else:
        rating = None
    
    # Extract brand
    brand_data = product.get('brand', {})
    if isinstance(brand_data, dict):
        brand = brand_data.get('name')
    else:
        brand = None
    
    # Extract offers/price
    offers = product.get('offers', {})
    if isinstance(offers, dict):
        price = offers.get('price')
        currency = offers.get('priceCurrency', 'USD')
        availability = offers.get('availability', '')
        in_stock = 'InStock' in availability
    else:
        price = None
        currency = 'USD'
        in_stock = None
    
    # Normalize image URL - remove any whitespace/newlines
    image_url = product.get('image', '')
    if image_url:
        # Remove all whitespace characters including newlines
        image_url = ''.join(image_url.split())
    
    return {
        'itemId': str(product.get('sku', '')),
        'name': product.get('name', ''),
        'description': product.get('description', ''),
        'brand': brand,
        'price': price,
        'currency': currency,
        'inStock': in_stock,
        'imageUrl': image_url,
        'rating': rating
    }


def process_html_file(html_file: Path, category_slug: str) -> list:
    """Process a single HTML file and extract all products"""
    print(f"\n📄 Processing: {html_file.parent.name}/index.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    products = extract_product_data_from_html(html_content)
    
    # Filter out products without itemId
    products = [p for p in products if p['itemId']]
    
    print(f"   ✅ Extracted {len(products)} products with full details")
    
    return products


def main():
    base_path = Path(__file__).parent.parent / '_scraped data' / 'THD Product Page Data'
    output_dir = Path(__file__).parent.parent / '_source data'
    
    print(f"\n{'='*70}")
    print(f"🔍 Extracting Complete Product Data from Saved HTML")
    print(f"{'='*70}")
    
    # Find all index.html files
    html_files = list(base_path.rglob('index.html'))
    
    # Filter out frame files
    html_files = [f for f in html_files if '/frames/' not in str(f)]
    
    print(f"\n📊 Found {len(html_files)} category HTML files")
    
    all_products = {}
    duplicate_count = 0
    
    for html_file in html_files:
        # Determine category from path
        rel_path = html_file.relative_to(base_path)
        category_slug = rel_path.parent.name.lower().replace(' ', '_').replace('-', '_')
        
        products = process_html_file(html_file, category_slug)
        
        for product in products:
            item_id = product['itemId']
            if item_id in all_products:
                duplicate_count += 1
                # Keep the one with more data
                if len(str(product)) > len(str(all_products[item_id])):
                    all_products[item_id] = product
            else:
                all_products[item_id] = product
    
    print(f"\n{'='*70}")
    print(f"✨ Extraction Complete!")
    print(f"{'='*70}")
    print(f"   Total unique products: {len(all_products)}")
    print(f"   Duplicate entries (merged): {duplicate_count}")
    
    # Save to pip-datasets.json
    output_file = output_dir / 'pip-datasets.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(all_products, f, indent=2)
    
    print(f"\n💾 Saved to: {output_file.relative_to(output_file.parent.parent)}")
    
    # Show sample data
    sample_products = list(all_products.values())[:3]
    print(f"\n📦 Sample products:")
    for product in sample_products:
        print(f"   • {product['itemId']}: {product['brand']} - {product['name'][:60]}...")
        print(f"     Price: ${product['price']} | Rating: {product['rating']['average'] if product['rating'] else 'N/A'}")
    
    # Stats by brand
    brands = {}
    for product in all_products.values():
        brand = product.get('brand') or 'Unknown'
        brands[brand] = brands.get(brand, 0) + 1
    
    print(f"\n📊 Top Brands:")
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {brand}: {count} products")


if __name__ == '__main__':
    main()
