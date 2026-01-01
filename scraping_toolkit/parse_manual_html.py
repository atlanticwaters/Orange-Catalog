#!/usr/bin/env python3
"""
Parse manually saved HTML files from Home Depot
Extracts product IDs and saves in the same format as automated scraper
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup


def extract_product_ids(html_content: str) -> list:
    """Extract product IDs from HTML content"""
    soup = BeautifulSoup(html_content, 'lxml')
    product_ids = []
    
    print("   🔍 Extracting product IDs...")
    
    # Method 1: data-product-id attributes
    for elem in soup.find_all(attrs={'data-product-id': True}):
        pid = elem.get('data-product-id')
        if pid and str(pid).isdigit() and len(str(pid)) >= 8 and pid not in product_ids:
            product_ids.append(str(pid))
    
    # Method 2: Links to product pages
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/p/' in href:
            # Extract product ID from URL
            matches = re.findall(r'/p/[^/]+/(\d{9,})', href)
            for pid in matches:
                if pid not in product_ids:
                    product_ids.append(pid)
    
    # Method 3: JSON-LD structured data
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                for field in ['sku', 'productID', 'itemId']:
                    if field in data:
                        pid = str(data[field])
                        if pid.isdigit() and len(pid) >= 8 and pid not in product_ids:
                            product_ids.append(pid)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        for field in ['sku', 'productID', 'itemId']:
                            if field in item:
                                pid = str(item[field])
                                if pid.isdigit() and len(pid) >= 8 and pid not in product_ids:
                                    product_ids.append(pid)
        except:
            continue
    
    # Method 4: Embedded JSON data
    for script in soup.find_all('script'):
        if script.string:
            matches = re.findall(r'"(?:productId|itemId|sku)":\s*"?(\d{9,})"?', script.string)
            for pid in matches:
                if pid not in product_ids:
                    product_ids.append(pid)
    
    return product_ids


def parse_html_file(html_file: Path, category_slug: str, output_dir: Path):
    """Parse a single HTML file and save results"""
    print(f"\n📄 Processing: {html_file.name}")
    
    # Read HTML
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract product IDs
    product_ids = extract_product_ids(html_content)
    
    print(f"   ✅ Found {len(product_ids)} products")
    
    # Create data structure
    data = {
        'categoryName': category_slug,
        'url': f"manually_saved_{html_file.name}",
        'scrapedAt': datetime.now().isoformat(),
        'productIds': product_ids,
        'totalProducts': len(product_ids),
    }
    
    # Create output directory
    cat_dir = output_dir / category_slug
    cat_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_file = cat_dir / f"{category_slug}_plp.json"
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"   💾 Saved to: {json_file}")
    
    # Save manifest
    manifest = {
        'timestamp': data['scrapedAt'],
        'url': data['url'],
        'productCount': len(product_ids),
        'totalProducts': len(product_ids),
    }
    
    manifest_file = cat_dir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    # Copy HTML file
    html_dest = cat_dir / f"{category_slug}_page.html"
    with open(html_dest, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"   💾 HTML copied: {html_dest}")
    
    return len(product_ids)


def main():
    parser = argparse.ArgumentParser(description='Parse manually saved HTML files')
    parser.add_argument('html_files', nargs='+', help='HTML files to parse')
    parser.add_argument('--category', required=True, help='Category slug (e.g., appliances_all)')
    parser.add_argument('--output', default='../_scraped data/Automated Scrapes/plp_data', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    total_products = 0
    
    print(f"\n📋 Processing {len(args.html_files)} HTML file(s)...")
    
    for html_path in args.html_files:
        html_file = Path(html_path)
        if not html_file.exists():
            print(f"   ❌ File not found: {html_file}")
            continue
        
        count = parse_html_file(html_file, args.category, output_dir)
        total_products += count
    
    print(f"\n{'='*70}")
    print(f"✨ Processing Complete!")
    print(f"   Total products found: {total_products}")
    print(f"   Output directory: {output_dir / args.category}")


if __name__ == '__main__':
    main()
