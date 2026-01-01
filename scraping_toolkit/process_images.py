#!/usr/bin/env python3
"""
Process and organize product images from saved HTML files
Maps images from _scraped data to production data/products/[id]/
"""

import json
import shutil
from pathlib import Path
from urllib.parse import urlparse
import re

def build_image_url_mapping(scraped_data_path: Path) -> dict:
    """Build a mapping of original URLs to local saved image files"""
    url_to_file = {}
    
    # Find all manifest.json files
    for manifest_file in scraped_data_path.rglob('manifest.json'):
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            resources = manifest.get('resources', {})
            folder = manifest_file.parent
            
            # Map each image resource
            for local_path, original_url in resources.items():
                if local_path.startswith('images/'):
                    full_local_path = folder / local_path
                    if full_local_path.exists():
                        url_to_file[original_url] = full_local_path
        except Exception as e:
            # Skip manifests that can't be read
            continue
    
    return url_to_file

def extract_filename_from_url(url: str) -> str:
    """Extract just the filename from image URL"""
    if not url:
        return None
    return url.split('/')[-1]

def find_image_for_url(image_url: str, url_mapping: dict) -> Path:
    """Find the local saved image file for a given URL"""
    if not image_url:
        return None
    
    # Direct match
    if image_url in url_mapping:
        return url_mapping[image_url]
    
    # Try without query parameters
    base_url = image_url.split('?')[0]
    if base_url in url_mapping:
        return url_mapping[base_url]
    
    # The product data has thumbnail URLs (64_100.jpg) but saved images
    # might be larger sizes (64_600.jpg, 64_300.jpg, etc.)
    # Try replacing the size suffix (Note: it's 64_100 not _64_100!)
    if '64_100.' in image_url:
        # Try common larger sizes
        for size in ['64_600.', '64_300.', '64_400.', '64_1000.']:
            alt_url = image_url.replace('64_100.', size)
            if alt_url in url_mapping:
                return url_mapping[alt_url]
    
    # Also try stripping the size entirely
    import re
    base_without_size = re.sub(r'-\d+_\d+\.(\w+)$', r'.\1', image_url)
    if base_without_size != image_url and base_without_size in url_mapping:
        return url_mapping[base_without_size]
    
    return None

def process_all_images():
    """Process and copy all product images"""
    
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    scraped_data_path = base_path / '_scraped data' / 'THD Product Page Data'
    production_path = base_path / 'production data'
    
    print('='*70)
    print('📸 Processing Product Images')
    print('='*70)
    print()
    
    # Load product data
    print('📂 Loading product data...')
    with open(base_path / '_source data' / 'pip-datasets.json', 'r') as f:
        products = json.load(f)
    print(f'   ✅ Loaded {len(products)} products')
    print()
    
    # Build image URL mapping from manifest files
    print('🗺️  Building image URL mapping from manifest files...')
    url_mapping = build_image_url_mapping(scraped_data_path)
    print(f'   ✅ Mapped {len(url_mapping):,} image URLs')
    print()
    
    # Statistics
    stats = {
        'total': len(products),
        'found': 0,
        'copied': 0,
        'missing': 0,
        'errors': 0
    }
    
    missing_images = []
    
    print('🔍 Copying product images...')
    for i, (product_id, product) in enumerate(products.items(), 1):
        if i % 100 == 0:
            print(f'   Processed {i}/{len(products)} products...')
        
        image_url = product.get('imageUrl')
        if not image_url:
            stats['missing'] += 1
            continue
        
        # Find image using URL mapping
        source_image = find_image_for_url(image_url, url_mapping)
        
        if source_image:
            stats['found'] += 1
            
            # Get original filename for destination
            filename = extract_filename_from_url(image_url)
            
            # Create product folder if it doesn't exist
            product_folder = production_path / 'products' / product_id
            product_folder.mkdir(parents=True, exist_ok=True)
            
            # Copy image to product folder with original filename
            dest_image = product_folder / filename
            try:
                if not dest_image.exists():
                    shutil.copy2(source_image, dest_image)
                    stats['copied'] += 1
            except Exception as e:
                print(f'   ⚠️  Error copying {filename}: {e}')
                stats['errors'] += 1
        else:
            stats['missing'] += 1
            missing_images.append({
                'product_id': product_id,
                'product_name': product.get('name', 'Unknown')[:60],
                'url': image_url[:80]
            })
    
    print()
    print('='*70)
    print('✨ Image Processing Complete!')
    print('='*70)
    print()
    print(f'   Total Products:     {stats["total"]:,}')
    print(f'   Images Found:       {stats["found"]:,}')
    print(f'   Images Copied:      {stats["copied"]:,}')
    print(f'   Images Missing:     {stats["missing"]:,}')
    print(f'   Errors:             {stats["errors"]:,}')
    print()
    
    if missing_images and len(missing_images) <= 20:
        print('Sample missing images:')
        for item in missing_images[:20]:
            print(f'   - {item["url"]}')
            print(f'     Product: {item["product_name"]}')
        if len(missing_images) > 20:
            print(f'   ... and {len(missing_images) - 20} more')
        print()
    
    return stats

if __name__ == '__main__':
    stats = process_all_images()
