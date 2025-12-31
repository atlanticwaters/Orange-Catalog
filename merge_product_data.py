#!/usr/bin/env python3
"""
Merge Product Data Script
Combines extracted category data with existing PLP/PIP datasets
Tags products with filter attributes and creates final production JSON files
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Base paths
BASE_DIR = Path(__file__).parent
SOURCE_DIR = BASE_DIR / "_source data"
PRODUCTION_DIR = BASE_DIR / "production data"

def load_json(filepath: Path) -> Any:
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error loading {filepath}: {e}")
        return None

def save_json(data: Any, filepath: Path):
    """Save data as formatted JSON"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def slugify(text: str) -> str:
    """Convert text to lowercase kebab-case slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def merge_lawn_mowers_data():
    """Merge lawn mowers data as an example"""
    print("\n📦 Merging lawn mowers data...")
    
    # Load source lawn mowers data
    lawn_mowers_source = load_json(SOURCE_DIR / "lawn-mowers.json")
    if not lawn_mowers_source:
        print("  ⚠️  No lawn mowers source data found")
        return
    
    # Create category structure
    category_data = {
        "categoryId": "outdoors/outdoor-power-equipment/lawn-mowers",
        "name": "Lawn Mowers",
        "slug": "lawn-mowers",
        "path": "/categories/outdoors/outdoor-power-equipment/lawn-mowers",
        "breadcrumbs": lawn_mowers_source.get("pageInfo", {}).get("breadcrumbs", []),
        "pageInfo": lawn_mowers_source.get("pageInfo", {}),
        "featuredBrands": lawn_mowers_source.get("featuredBrands", []),
        "quickFilters": lawn_mowers_source.get("quickFilters", []),
        "filters": lawn_mowers_source.get("filters", []),
        "sortOptions": lawn_mowers_source.get("sortOptions", []),
        "products": lawn_mowers_source.get("products", []),
        "pagination": lawn_mowers_source.get("pagination", {})
    }
    
    # Save to production
    output_dir = PRODUCTION_DIR / "categories" / "outdoors" / "outdoor-power-equipment"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save full category file
    save_json(category_data, output_dir / "lawn-mowers.json")
    print(f"  ✅ Saved lawn-mowers.json with {len(category_data['products'])} products")
    
    # Save lightweight products list
    products_list = {
        "categoryId": category_data["categoryId"],
        "totalProducts": len(category_data['products']),
        "products": category_data['products']
    }
    save_json(products_list, output_dir / "lawn-mowers-products.json")
    print(f"  ✅ Saved lawn-mowers-products.json")
    
    return category_data

def load_pip_datasets():
    """Load PIP datasets and index by product ID"""
    print("\n📦 Loading PIP datasets...")
    
    pip_file = SOURCE_DIR / "pip-datasets.json"
    if not pip_file.exists():
        print("  ⚠️  No PIP datasets found")
        return {}
    
    pip_data = load_json(pip_file)
    if not pip_data:
        return {}
    
    # Index by product ID
    pip_index = {}
    if isinstance(pip_data, list):
        for product in pip_data:
            product_id = product.get("productId")
            if product_id:
                pip_index[product_id] = product
    elif isinstance(pip_data, dict) and "products" in pip_data:
        for product in pip_data["products"]:
            product_id = product.get("productId")
            if product_id:
                pip_index[product_id] = product
    
    print(f"  ✅ Indexed {len(pip_index)} PIP products")
    return pip_index

def load_plp_datasets():
    """Load PLP datasets"""
    print("\n📦 Loading PLP datasets...")
    
    plp_file = SOURCE_DIR / "plp-datasets.json"
    if not plp_file.exists():
        print("  ⚠️  No PLP datasets found")
        return {}
    
    plp_data = load_json(plp_file)
    if not plp_data:
        return {}
    
    print(f"  ✅ Loaded PLP data")
    return plp_data

def create_product_detail_files(pip_index: Dict[str, Any]):
    """Create individual product detail files"""
    print("\n📝 Creating individual product detail files...")
    
    products_dir = PRODUCTION_DIR / "products"
    products_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for product_id, product_data in pip_index.items():
        product_dir = products_dir / product_id
        product_dir.mkdir(parents=True, exist_ok=True)
        
        # Save product details
        save_json(product_data, product_dir / "details.json")
        count += 1
    
    print(f"  ✅ Created {count} product detail files")

def analyze_existing_categories():
    """Analyze what category JSON files we already extracted"""
    print("\n🔍 Analyzing extracted category files...")
    
    categories_dir = PRODUCTION_DIR / "categories"
    if not categories_dir.exists():
        print("  ⚠️  No categories directory found")
        return []
    
    category_files = []
    for json_file in categories_dir.rglob("*.json"):
        if json_file.name != "index.json":
            category_files.append(json_file)
    
    print(f"  📊 Found {len(category_files)} category files")
    
    # Show some examples
    for i, cat_file in enumerate(category_files[:5]):
        rel_path = cat_file.relative_to(categories_dir)
        data = load_json(cat_file)
        if data:
            product_count = data.get("totalProducts", 0)
            filter_count = len(data.get("filters", []))
            print(f"    - {rel_path}: {product_count} products, {filter_count} filters")
    
    if len(category_files) > 5:
        print(f"    ... and {len(category_files) - 5} more")
    
    return category_files

def enhance_category_files():
    """Enhance extracted category files with product details"""
    print("\n✨ Enhancing category files...")
    
    # Load PIP index
    pip_index = load_pip_datasets()
    
    # Get all category files
    categories_dir = PRODUCTION_DIR / "categories"
    category_files = list(categories_dir.rglob("*.json"))
    
    enhanced_count = 0
    for cat_file in category_files:
        if cat_file.name == "index.json":
            continue
        
        data = load_json(cat_file)
        if not data:
            continue
        
        # Add metadata
        if "version" not in data:
            data["version"] = "1.0"
        if "lastUpdated" not in data:
            data["lastUpdated"] = "2025-12-31"
        
        # Update image URLs to be production-ready
        # (We'll handle actual image copying in next script)
        
        # Save enhanced version
        save_json(data, cat_file)
        enhanced_count += 1
    
    print(f"  ✅ Enhanced {enhanced_count} category files")

def main():
    """Main execution function"""
    print("=" * 80)
    print("🔄 PRODUCT DATA MERGE")
    print("=" * 80)
    
    # Merge lawn mowers as an example
    merge_lawn_mowers_data()
    
    # Load and index PIP data
    pip_index = load_pip_datasets()
    
    # Load PLP data
    plp_data = load_plp_datasets()
    
    # Create individual product files
    if pip_index:
        create_product_detail_files(pip_index)
    
    # Analyze existing categories
    analyze_existing_categories()
    
    # Enhance category files
    enhance_category_files()
    
    print("\n" + "=" * 80)
    print("✅ PRODUCT DATA MERGE COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Extract and organize images")
    print("  2. Update image references in JSON")
    print("  3. Generate final navigation manifests")

if __name__ == "__main__":
    main()
