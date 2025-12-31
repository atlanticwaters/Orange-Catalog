#!/usr/bin/env python3
"""
Validation Script
Validates JSON structure and reports on data quality
"""

import json
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).parent
PRODUCTION_DIR = BASE_DIR / "production data"

def load_json(filepath: Path) -> Any:
    """Load JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def validate_category_files():
    """Validate all category JSON files"""
    print("\n🔍 Validating category files...")
    
    categories_dir = PRODUCTION_DIR / "categories"
    valid_count = 0
    invalid_count = 0
    issues = []
    
    for json_file in categories_dir.rglob("*.json"):
        data = load_json(json_file)
        if data is None:
            invalid_count += 1
            issues.append(f"Failed to load: {json_file.name}")
            continue
        
        # Check required fields
        required_fields = ["categoryId", "name"]
        missing_fields = [f for f in required_fields if f not in data]
        
        if missing_fields:
            invalid_count += 1
            issues.append(f"{json_file.name}: Missing {missing_fields}")
        else:
            valid_count += 1
    
    print(f"  ✅ Valid: {valid_count}")
    print(f"  ❌ Invalid: {invalid_count}")
    
    if issues:
        print("\n  Issues found:")
        for issue in issues[:10]:  # Show first 10
            print(f"    - {issue}")
        if len(issues) > 10:
            print(f"    ... and {len(issues) - 10} more")
    
    return valid_count, invalid_count

def validate_product_files():
    """Validate product detail files"""
    print("\n🔍 Validating product files...")
    
    products_dir = PRODUCTION_DIR / "products"
    if not products_dir.exists():
        print("  ⚠️  No products directory")
        return 0, 0
    
    valid_count = 0
    invalid_count = 0
    
    for product_dir in products_dir.iterdir():
        if not product_dir.is_dir():
            continue
        
        details_file = product_dir / "details.json"
        if not details_file.exists():
            invalid_count += 1
            continue
        
        data = load_json(details_file)
        if data and "productId" in data:
            valid_count += 1
        else:
            invalid_count += 1
    
    print(f"  ✅ Valid: {valid_count}")
    print(f"  ❌ Invalid: {invalid_count}")
    
    return valid_count, invalid_count

def check_images():
    """Check image organization"""
    print("\n🔍 Checking images...")
    
    images_dir = PRODUCTION_DIR / "images"
    if not images_dir.exists():
        print("  ⚠️  No images directory")
        return
    
    for subdir in ["products", "brands", "ui", "heroes"]:
        path = images_dir / subdir
        if path.exists():
            count = len(list(path.iterdir()))
            print(f"  📸 {subdir}: {count} files")

def generate_stats():
    """Generate comprehensive stats"""
    print("\n📊 Generating statistics...")
    
    stats = {
        "categories": {},
        "products": {},
        "filters": {},
        "brands": set()
    }
    
    # Analyze categories
    categories_dir = PRODUCTION_DIR / "categories"
    if categories_dir.exists():
        for json_file in categories_dir.rglob("*.json"):
            if json_file.name == "index.json":
                continue
            
            data = load_json(json_file)
            if not data:
                continue
            
            # Count products
            product_count = data.get("totalProducts", len(data.get("products", [])))
            category_id = data.get("categoryId", json_file.stem)
            stats["categories"][category_id] = product_count
            
            # Count filters
            filter_count = len(data.get("filters", []))
            if filter_count > 0:
                stats["filters"][category_id] = filter_count
            
            # Collect brands
            for brand in data.get("featuredBrands", []):
                stats["brands"].add(brand.get("brandName"))
    
    print(f"  📁 Total categories: {len(stats['categories'])}")
    print(f"  📦 Total products across all categories: {sum(stats['categories'].values())}")
    print(f"  🔧 Categories with filters: {len(stats['filters'])}")
    print(f"  🏷️  Unique brands: {len(stats['brands'])}")
    
    # Top categories by product count
    top_categories = sorted(stats["categories"].items(), key=lambda x: x[1], reverse=True)[:10]
    if top_categories:
        print("\n  📈 Top 10 categories by product count:")
        for cat_id, count in top_categories:
            print(f"     {count:3d} products - {cat_id}")

def main():
    """Main validation"""
    print("=" * 80)
    print("✅ DATA VALIDATION")
    print("=" * 80)
    
    # Validate categories
    cat_valid, cat_invalid = validate_category_files()
    
    # Validate products
    prod_valid, prod_invalid = validate_product_files()
    
    # Check images
    check_images()
    
    # Generate stats
    generate_stats()
    
    print("\n" + "=" * 80)
    print("✅ VALIDATION COMPLETE")
    print("=" * 80)
    
    total_issues = cat_invalid + prod_invalid
    if total_issues == 0:
        print("\n🎉 No issues found! Data is ready for deployment.")
    else:
        print(f"\n⚠️  Found {total_issues} issues that need attention.")

if __name__ == "__main__":
    main()
