#!/usr/bin/env python3
"""
Filter products to only include those with local images
Creates a new filtered dataset and regenerates production data
"""

import json
import shutil
from pathlib import Path

def filter_products_with_images():
    """Filter products to only include those with local images"""
    
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    
    print('='*70)
    print('🔍 Filtering Products - Keeping Only Those With Images')
    print('='*70)
    print()
    
    # Load all products
    print('📂 Loading product data...')
    with open(base_path / '_source data' / 'pip-datasets.json', 'r') as f:
        all_products = json.load(f)
    print(f'   ✅ Loaded {len(all_products):,} total products')
    print()
    
    # Filter to only products with local images
    print('🖼️  Filtering products with local images...')
    filtered_products = {}
    
    for pid, product in all_products.items():
        product_folder = base_path / 'production data' / 'products' / pid
        url = product.get('imageUrl', '')
        
        if url:
            filename = url.split('/')[-1]
            if (product_folder / filename).exists():
                filtered_products[pid] = product
    
    print(f'   ✅ Found {len(filtered_products):,} products with images')
    print(f'   ❌ Removed {len(all_products) - len(filtered_products):,} products without images')
    print()
    
    # Backup original file
    print('💾 Creating backup of original data...')
    backup_path = base_path / '_source data' / 'pip-datasets-full.json'
    shutil.copy2(
        base_path / '_source data' / 'pip-datasets.json',
        backup_path
    )
    print(f'   ✅ Backed up to: {backup_path.name}')
    print()
    
    # Save filtered dataset
    print('💾 Saving filtered dataset...')
    with open(base_path / '_source data' / 'pip-datasets.json', 'w') as f:
        json.dump(filtered_products, f, indent=2)
    print(f'   ✅ Saved {len(filtered_products):,} products')
    print()
    
    # Remove product folders without images
    print('🗑️  Removing product folders without images...')
    removed_folders = 0
    products_dir = base_path / 'production data' / 'products'
    
    for product_folder in products_dir.iterdir():
        if product_folder.is_dir():
            pid = product_folder.name
            if pid not in filtered_products:
                shutil.rmtree(product_folder)
                removed_folders += 1
    
    print(f'   ✅ Removed {removed_folders:,} product folders')
    print()
    
    print('='*70)
    print('✨ Filtering Complete!')
    print('='*70)
    print()
    print(f'   Products in dataset:        {len(filtered_products):,}')
    print(f'   Products removed:           {len(all_products) - len(filtered_products):,}')
    print(f'   Image coverage:             100%')
    print()
    print('📋 Next step: Re-run transform_to_production.py to update categories')
    print()
    
    return len(filtered_products), len(all_products) - len(filtered_products)

if __name__ == '__main__':
    kept, removed = filter_products_with_images()
