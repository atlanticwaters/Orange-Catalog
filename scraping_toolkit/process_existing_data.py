#!/usr/bin/env python3
"""
Process existing scraped data from _scraped data directory
This is faster and more reliable than re-scraping!
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
SCRAPED_BASE = BASE_DIR / "_scraped data" / "THD Product Page Data"
OUTPUT_DIR = BASE_DIR / "_scraped data" / "Processed Scrapes"
PROD_DATA_DIR = BASE_DIR / "production data"

def process_existing_scraped_data():
    """Process your existing scraped PLP and PIP data"""
    
    print("🔄 Processing Existing Scraped Data\n")
    print("="*70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    stats = {
        'categories_processed': 0,
        'products_found': 0,
        'images_found': 0,
    }
    
    # Process Refrigerator subcategories (you have these!)
    fridge_dir = SCRAPED_BASE / "Fridge PLP" / "Fridge PLP Items"
    
    if fridge_dir.exists():
        print(f"\n📂 Processing Refrigerator Categories from: {fridge_dir}\n")
        
        for subcat_dir in fridge_dir.iterdir():
            if not subcat_dir.is_dir():
                continue
            
            category_name = subcat_dir.name
            print(f"   Processing: {category_name}")
            
            # Look for manifest.json files
            manifests = list(subcat_dir.rglob("manifest.json"))
            
            for manifest_file in manifests:
                try:
                    with open(manifest_file) as f:
                        manifest = json.load(f)
                    
                    # Check for product data
                    productData = manifest.get('productData', [])
                    print(f"      → Found {len(productData)} products")
                    
                    stats['products_found'] += len(productData)
                    stats['categories_processed'] += 1
                    
                except Exception as e:
                    print(f"      ❌ Error: {e}")
    
    # Process Tool Categories
    tool_dir = SCRAPED_BASE / "Tool Categories"
    
    if tool_dir.exists():
        print(f"\n📂 Processing Tool Categories from: {tool_dir}\n")
        
        for subcat_dir in tool_dir.iterdir():
            if not subcat_dir.is_dir():
                continue
            
            category_name = subcat_dir.name
            manifests = list(subcat_dir.rglob("manifest.json"))
            
            if manifests:
                print(f"   {category_name}: {len(manifests)} manifest(s)")
                stats['categories_processed'] += 1
    
    # Process PLP Landing Pages
    plp_dir = SCRAPED_BASE / "PLP Landing Pages"
    
    if plp_dir.exists():
        print(f"\n📂 Processing PLP Landing Pages from: {plp_dir}\n")
        
        for subcat_dir in plp_dir.iterdir():
            if not subcat_dir.is_dir():
                continue
            
            category_name = subcat_dir.name
            manifests = list(subcat_dir.rglob("manifest.json"))
            
            if manifests:
                print(f"   {category_name}: {len(manifests)} manifest(s)")
                stats['categories_processed'] += 1
    
    # Summary
    print(f"\n{'='*70}")
    print(f"✨ Processing Complete!\n")
    print(f"   Categories with data: {stats['categories_processed']}")
    print(f"   Products found: {stats['products_found']}")
    
    print(f"\n💡 RECOMMENDATION:")
    print(f"   You already have scraped data in: {SCRAPED_BASE}")
    print(f"   Instead of re-scraping, run your existing transformation scripts:")
    print(f"\n   cd '{BASE_DIR}'")
    print(f"   python3 extract_category_data.py")
    print(f"   python3 finalize_production_data.py")
    

def suggest_next_categories():
    """Suggest which categories to manually scrape next"""
    
    print(f"\n{'='*70}")
    print("📝 SUGGESTED MANUAL SCRAPING TARGETS:\n")
    
    suggestions = {
        "High Value Appliances (Missing)": [
            "Side by Side Refrigerators - Already have folder, just need to scrape",
            "Top Freezer Refrigerators - Already have folder",
            "Bottom Freezer Refrigerators - Already have folder",
            "French Door Refrigerators - Already have folder",
        ],
        "Quick Wins (Small Categories)": [
            "Dishwashers - Only 7 products currently",
            "Ranges - Only 4 products currently",
            "Wall Ovens - Only 8 products currently",
        ]
    }
    
    for category, items in suggestions.items():
        print(f"   {category}:")
        for item in items:
            print(f"      • {item}")
        print()
    
    print("   💡 TIP: Use browser extensions like 'SingleFile' or 'Save Page WE'")
    print("      to manually save PLP pages as complete HTML files, then process them!")


if __name__ == '__main__':
    process_existing_scraped_data()
    suggest_next_categories()
