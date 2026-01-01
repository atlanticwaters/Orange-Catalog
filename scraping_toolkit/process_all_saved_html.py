#!/usr/bin/env python3
"""
Batch process all manually saved HTML files
Walks through directory structure and extracts product IDs from all index.html files
"""

import json
import re
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict


def extract_product_ids(html_content: str) -> list:
    """Extract product IDs from HTML content"""
    soup = BeautifulSoup(html_content, 'lxml')
    product_ids = []
    
    # Method 1: data-product-id attributes
    for elem in soup.find_all(attrs={'data-product-id': True}):
        pid = elem.get('data-product-id')
        if pid and str(pid).isdigit() and len(str(pid)) >= 8 and pid not in product_ids:
            product_ids.append(str(pid))
    
    # Method 2: Links to product pages
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/p/' in href:
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


def slugify(name: str) -> str:
    """Convert category name to slug"""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '_', slug)
    return slug.strip('_')


def process_category_folder(category_path: Path, output_dir: Path) -> dict:
    """Process a single category folder containing index.html"""
    html_file = category_path / 'index.html'
    
    if not html_file.exists():
        return None
    
    category_name = category_path.name
    category_slug = slugify(category_name)
    
    print(f"\n📁 {category_name}")
    print(f"   📄 Reading: {html_file.relative_to(category_path.parent.parent.parent)}")
    
    # Read HTML
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return None
    
    # Extract product IDs
    product_ids = extract_product_ids(html_content)
    
    print(f"   ✅ Found {len(product_ids)} products")
    
    if len(product_ids) == 0:
        print(f"   ⚠️  No products found - skipping")
        return None
    
    # Create data structure
    data = {
        'categoryName': category_name,
        'categorySlug': category_slug,
        'url': str(category_path.relative_to(category_path.parent.parent.parent)),
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
    
    # Save manifest
    manifest = {
        'timestamp': data['scrapedAt'],
        'sourcePath': str(category_path),
        'url': data['url'],
        'productCount': len(product_ids),
        'totalProducts': len(product_ids),
    }
    
    manifest_file = cat_dir / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"   💾 Saved to: {cat_dir.relative_to(output_dir.parent)}")
    
    return {
        'category': category_name,
        'slug': category_slug,
        'products': len(product_ids),
        'productIds': product_ids
    }


def find_all_html_folders(base_path: Path) -> list:
    """Find all folders containing index.html files"""
    html_folders = []
    
    for item in base_path.rglob('index.html'):
        html_folders.append(item.parent)
    
    return sorted(html_folders)


def main():
    base_path = Path(__file__).parent.parent / '_scraped data' / 'THD Product Page Data'
    output_dir = Path(__file__).parent.parent / '_scraped data' / 'Automated Scrapes' / 'plp_data'
    
    print(f"\n{'='*70}")
    print(f"🔍 Scanning for HTML files in:")
    print(f"   {base_path}")
    print(f"{'='*70}")
    
    # Find all folders with index.html
    html_folders = find_all_html_folders(base_path)
    
    print(f"\n📊 Found {len(html_folders)} category folders with HTML files")
    
    # Process each folder
    results = []
    all_product_ids = set()
    
    for folder in html_folders:
        result = process_category_folder(folder, output_dir)
        if result:
            results.append(result)
            all_product_ids.update(result['productIds'])
    
    # Summary
    print(f"\n{'='*70}")
    print(f"✨ Processing Complete!")
    print(f"{'='*70}")
    print(f"   Categories processed: {len(results)}")
    print(f"   Total products found: {len(all_product_ids)}")
    print(f"   Output directory: {output_dir}")
    
    # Show breakdown by parent folder
    by_parent = defaultdict(lambda: {'count': 0, 'products': 0})
    for result in results:
        # Find which parent folder this came from
        for folder in html_folders:
            if result['slug'] == slugify(folder.name):
                parent = folder.parent.name
                by_parent[parent]['count'] += 1
                by_parent[parent]['products'] += result['products']
                break
    
    print(f"\n📦 Breakdown by folder:")
    for parent, stats in sorted(by_parent.items()):
        print(f"   {parent}:")
        print(f"      Categories: {stats['count']}")
        print(f"      Products: {stats['products']}")
    
    # Save summary
    summary = {
        'processedAt': datetime.now().isoformat(),
        'totalCategories': len(results),
        'totalUniqueProducts': len(all_product_ids),
        'categories': results,
        'breakdown': dict(by_parent)
    }
    
    summary_file = output_dir / 'batch_processing_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Summary saved to: {summary_file.relative_to(output_dir.parent)}")


if __name__ == '__main__':
    main()
