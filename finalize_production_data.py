#!/usr/bin/env python3
"""
Final Data Processing Script
- Extracts and organizes 600px images + SVG logos
- Updates all JSON files with proper image URLs
- Creates individual product detail files with full PIP data
- Generates final navigation manifests
"""

import json
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from urllib.parse import urlparse, unquote

# Base paths
BASE_DIR = Path(__file__).parent
SCRAPED_DIR = BASE_DIR / "_scraped data" / "THD Product Page Data"
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

def is_600px_image(url: str, filename: str) -> bool:
    """Check if image is 600px size"""
    # Check for _600 in URL
    if '_600' in url or '600' in url:
        return True
    # Check for 703px (THD's common size)
    if '703' in url:
        return True
    # Check filename patterns
    if '600' in filename:
        return True
    return False

def is_svg(filename: str, url: str) -> bool:
    """Check if file is SVG"""
    return filename.endswith('.svg') or url.endswith('.svg')

def extract_images_from_manifests():
    """Extract 600px images and SVGs from all manifests"""
    print("\n📸 Extracting images from manifests...")
    
    images_to_copy = []
    stats = {
        "600px": 0,
        "svg": 0,
        "other": 0,
        "total_manifests": 0
    }
    
    # Scan all manifest files
    for manifest_file in SCRAPED_DIR.rglob("manifest.json"):
        stats["total_manifests"] += 1
        manifest = load_json(manifest_file)
        if not manifest or "resources" not in manifest:
            continue
        
        manifest_dir = manifest_file.parent
        
        # Process each resource
        for filename, url in manifest["resources"].items():
            # Skip fonts, stylesheets, etc.
            if any(filename.startswith(x) for x in ["fonts/", "stylesheet", "frames/"]):
                continue
            
            # Check if it's a 600px image or SVG
            if is_svg(filename, url):
                stats["svg"] += 1
                images_to_copy.append({
                    "source": manifest_dir / filename,
                    "url": url,
                    "filename": filename,
                    "type": "svg"
                })
            elif "images/" in filename and is_600px_image(url, filename):
                stats["600px"] += 1
                images_to_copy.append({
                    "source": manifest_dir / filename,
                    "url": url,
                    "filename": filename,
                    "type": "600px"
                })
            else:
                stats["other"] += 1
    
    print(f"  📊 Scanned {stats['total_manifests']} manifests")
    print(f"  📸 Found {stats['600px']} @ 600px images")
    print(f"  🎨 Found {stats['svg']} SVG files")
    print(f"  ⏭️  Skipped {stats['other']} other files")
    
    return images_to_copy

def categorize_images(images: List[Dict]) -> Dict[str, List]:
    """Categorize images by type"""
    print("\n📂 Categorizing images...")
    
    categorized = {
        "products": [],
        "brands": [],
        "ui": [],
        "heroes": [],
        "uncategorized": []
    }
    
    for img in images:
        url = img["url"].lower()
        
        if "productimages" in url or "catalog/productImages" in url:
            categorized["products"].append(img)
        elif "brandlogos" in url or "logo" in url:
            categorized["brands"].append(img)
        elif "badge" in url or "icon" in url or "star" in url:
            categorized["ui"].append(img)
        elif "hero" in url or "banner" in url or "dam.thdstatic" in url:
            categorized["heroes"].append(img)
        else:
            categorized["uncategorized"].append(img)
    
    for category, items in categorized.items():
        if items:
            print(f"  - {category}: {len(items)} files")
    
    return categorized

def copy_images(categorized_images: Dict[str, List]):
    """Copy images to production directory"""
    print("\n📦 Copying images to production directory...")
    
    copied_count = 0
    skipped_count = 0
    
    for category, images in categorized_images.items():
        if category == "uncategorized":
            continue
        
        target_dir = PRODUCTION_DIR / "images" / category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for img in images:
            source = img["source"]
            if not source.exists():
                skipped_count += 1
                continue
            
            # Generate a better filename based on URL
            filename = img["filename"]
            if "/" in filename:
                filename = filename.split("/")[-1]
            
            target = target_dir / filename
            
            try:
                if not target.exists():
                    shutil.copy2(source, target)
                    copied_count += 1
            except Exception as e:
                print(f"  ⚠️  Error copying {source}: {e}")
                skipped_count += 1
    
    print(f"  ✅ Copied {copied_count} images")
    if skipped_count > 0:
        print(f"  ⏭️  Skipped {skipped_count} images (missing or error)")

def load_pip_data() -> Dict[str, Any]:
    """Load and index PIP data"""
    print("\n📦 Loading PIP product data...")
    
    pip_file = SOURCE_DIR / "pip-datasets.json"
    if not pip_file.exists():
        print("  ⚠️  No PIP data found")
        return {}
    
    data = load_json(pip_file)
    if not data:
        return {}
    
    # Handle different formats
    pip_index = {}
    if isinstance(data, dict) and "pipDatasets" in data:
        for product in data["pipDatasets"]:
            product_id = product.get("productId")
            if product_id:
                pip_index[product_id] = product
    elif isinstance(data, list):
        for product in data:
            product_id = product.get("productId")
            if product_id:
                pip_index[product_id] = product
    
    print(f"  ✅ Indexed {len(pip_index)} products")
    return pip_index

def create_product_detail_files(pip_index: Dict[str, Any]):
    """Create individual product detail JSON files"""
    print("\n📝 Creating product detail files...")
    
    products_dir = PRODUCTION_DIR / "products"
    products_dir.mkdir(parents=True, exist_ok=True)
    
    count = 0
    for product_id, product_data in pip_index.items():
        product_dir = products_dir / product_id
        product_dir.mkdir(parents=True, exist_ok=True)
        
        # Save product details
        save_json(product_data, product_dir / "details.json")
        count += 1
        
        if count % 100 == 0:
            print(f"  ... {count} products processed")
    
    print(f"  ✅ Created {count} product detail files")

def update_navigation_index():
    """Update the main navigation index with accurate counts"""
    print("\n🗺️  Updating navigation index...")
    
    index_file = PRODUCTION_DIR / "categories" / "index.json"
    if not index_file.exists():
        print("  ⚠️  Index file not found")
        return
    
    index_data = load_json(index_file)
    if not index_data:
        return
    
    # Count products in each category
    categories_dir = PRODUCTION_DIR / "categories"
    
    for dept in index_data.get("departments", []):
        dept_slug = dept["slug"]
        
        # Count products in department
        dept_count = 0
        
        for subcat in dept.get("subcategories", []):
            subcat_slug = subcat["slug"]
            
            # Look for category JSON file
            possible_paths = [
                categories_dir / dept_slug / f"{subcat_slug}.json",
                categories_dir / f"{dept_slug}-{subcat_slug}.json",
            ]
            
            for path in possible_paths:
                if path.exists():
                    cat_data = load_json(path)
                    if cat_data:
                        product_count = cat_data.get("totalProducts", 0)
                        subcat["productCount"] = product_count
                        dept_count += product_count
                    break
        
        dept["productCount"] = dept_count
    
    # Save updated index
    save_json(index_data, index_file)
    print(f"  ✅ Updated navigation index")

def create_summary_report():
    """Create a summary report of the processed data"""
    print("\n📊 Creating summary report...")
    
    stats = {
        "categories": 0,
        "products": 0,
        "images": {
            "products": 0,
            "brands": 0,
            "ui": 0,
            "heroes": 0
        }
    }
    
    # Count categories
    categories_dir = PRODUCTION_DIR / "categories"
    if categories_dir.exists():
        stats["categories"] = len(list(categories_dir.rglob("*.json")))
    
    # Count products
    products_dir = PRODUCTION_DIR / "products"
    if products_dir.exists():
        stats["products"] = len(list(products_dir.glob("*")))
    
    # Count images
    images_dir = PRODUCTION_DIR / "images"
    if images_dir.exists():
        for img_type in ["products", "brands", "ui", "heroes"]:
            type_dir = images_dir / img_type
            if type_dir.exists():
                stats["images"][img_type] = len(list(type_dir.glob("*")))
    
    # Save report
    report_file = PRODUCTION_DIR / "SUMMARY.json"
    save_json(stats, report_file)
    
    print(f"\n{'='*80}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*80}")
    print(f"  📁 Categories: {stats['categories']}")
    print(f"  📦 Products: {stats['products']}")
    print(f"  📸 Images:")
    for img_type, count in stats["images"].items():
        print(f"     - {img_type}: {count}")
    print(f"{'='*80}\n")

def main():
    """Main execution"""
    print("=" * 80)
    print("🎯 FINAL DATA PROCESSING")
    print("=" * 80)
    
    # Step 1: Extract images
    images = extract_images_from_manifests()
    
    # Step 2: Categorize images
    categorized = categorize_images(images)
    
    # Step 3: Copy images to production
    copy_images(categorized)
    
    # Step 4: Load PIP data
    pip_index = load_pip_data()
    
    # Step 5: Create product detail files
    if pip_index:
        create_product_detail_files(pip_index)
    
    # Step 6: Update navigation index
    update_navigation_index()
    
    # Step 7: Create summary report
    create_summary_report()
    
    print("\n" + "=" * 80)
    print("✅ FINAL DATA PROCESSING COMPLETE!")
    print("=" * 80)
    print("\nProduction data is ready in: production data/")
    print("  - categories/    Category JSON files with filters")
    print("  - products/      Individual product details")
    print("  - images/        600px images + SVG logos")
    print("  - SUMMARY.json   Statistics and counts")

if __name__ == "__main__":
    main()
