#!/usr/bin/env python3
"""
Orange Catalog Data Transformation Script
Transforms scraped Home Depot data into production-ready structure for GitHub Pages & iOS app
"""

import json
import os
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import html

# Base paths
BASE_DIR = Path(__file__).parent
SCRAPED_DIR = BASE_DIR / "_scraped data" / "THD Product Page Data"
SOURCE_DIR = BASE_DIR / "_source data"
PRODUCTION_DIR = BASE_DIR / "production data"

# Department names (15 top-level)
DEPARTMENTS = [
    "Appliances", "Bath", "Building Materials", "Cleaning", "Electrical",
    "Flooring", "Garage", "Garden Center", "Home Decor", "Kitchen",
    "Lighting", "Plumbing", "Storage & Organization", "Tools", "Window Treatments"
]


def slugify(text: str) -> str:
    """Convert text to lowercase kebab-case slug"""
    # Remove special characters, convert to lowercase
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = text.strip('-')
    return text


def create_directory_structure():
    """Create the production data directory structure"""
    print("📁 Creating production data directory structure...")
    
    # Create main directories
    dirs = [
        PRODUCTION_DIR / "categories",
        PRODUCTION_DIR / "products",
        PRODUCTION_DIR / "images" / "categories",
        PRODUCTION_DIR / "images" / "brands",
        PRODUCTION_DIR / "images" / "ui",
        PRODUCTION_DIR / "brands"
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create department subdirectories
    for dept in DEPARTMENTS:
        dept_slug = slugify(dept)
        dept_dir = PRODUCTION_DIR / "categories" / dept_slug
        dept_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Created {len(dirs) + len(DEPARTMENTS)} directories")


def scan_scraped_categories() -> Dict[str, List[str]]:
    """Scan scraped data to build category hierarchy"""
    print("\n🔍 Scanning scraped data for categories...")
    
    categories = {
        "top_level": [],
        "plp_landing": [],
        "tool_categories": [],
        "fridge_types": []
    }
    
    # Scan Top Level THD Pages
    top_level_dir = SCRAPED_DIR / "Top Level THD Pages"
    if top_level_dir.exists():
        categories["top_level"] = [
            d.name for d in top_level_dir.iterdir() 
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    # Scan PLP Landing Pages
    plp_dir = SCRAPED_DIR / "PLP Landing Pages"
    if plp_dir.exists():
        categories["plp_landing"] = [
            d.name for d in plp_dir.iterdir() 
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    # Scan Tool Categories
    tools_dir = SCRAPED_DIR / "Tool Categories"
    if tools_dir.exists():
        categories["tool_categories"] = [
            d.name for d in tools_dir.iterdir() 
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    # Scan Fridge PLP Items
    fridge_dir = SCRAPED_DIR / "Fridge PLP" / "Fridge PLP Items"
    if fridge_dir.exists():
        categories["fridge_types"] = [
            d.name for d in fridge_dir.iterdir() 
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    print(f"  📊 Found:")
    print(f"     - {len(categories['top_level'])} top-level departments")
    print(f"     - {len(categories['plp_landing'])} PLP landing pages")
    print(f"     - {len(categories['tool_categories'])} tool categories")
    print(f"     - {len(categories['fridge_types'])} fridge types")
    print(f"  📈 Total: {sum(len(v) for v in categories.values())} categories")
    
    return categories


def build_category_taxonomy(categories: Dict[str, List[str]]) -> Dict[str, Any]:
    """Build hierarchical category taxonomy with human-readable IDs"""
    print("\n🏗️  Building category taxonomy...")
    
    taxonomy = {
        "version": "1.0",
        "lastUpdated": "2025-12-31",
        "departments": []
    }
    
    # Map departments to their subcategories
    dept_map = {
        "appliances": categories["plp_landing"] + categories["fridge_types"],
        "tools": categories["tool_categories"],
    }
    
    # Create department entries
    for dept_name in categories["top_level"]:
        dept_slug = slugify(dept_name)
        
        dept_entry = {
            "id": dept_slug,
            "name": dept_name,
            "slug": dept_slug,
            "path": f"/categories/{dept_slug}",
            "subcategories": []
        }
        
        # Add subcategories if available
        if dept_slug in dept_map:
            for subcat_name in sorted(set(dept_map[dept_slug])):
                subcat_slug = slugify(subcat_name)
                subcat_entry = {
                    "id": f"{dept_slug}/{subcat_slug}",
                    "name": subcat_name,
                    "slug": subcat_slug,
                    "path": f"/categories/{dept_slug}/{subcat_slug}",
                    "parent": dept_slug
                }
                dept_entry["subcategories"].append(subcat_entry)
        
        taxonomy["departments"].append(dept_entry)
    
    print(f"✅ Built taxonomy with {len(taxonomy['departments'])} departments")
    
    return taxonomy


def read_manifest(manifest_path: Path) -> Optional[Dict]:
    """Read and parse a manifest.json file"""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Error reading {manifest_path}: {e}")
        return None


def extract_category_id_from_url(url: str) -> Optional[str]:
    """Extract Home Depot category ID from URL (e.g., N-5yc1vZc3oo)"""
    match = re.search(r'N-([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None


def save_json(data: Any, filepath: Path):
    """Save data as formatted JSON"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_existing_products() -> Dict[str, Any]:
    """Load existing product data from source files"""
    print("\n📦 Loading existing product data...")
    
    products = {
        "plp": [],
        "pip": []
    }
    
    # Load PLP datasets
    plp_file = SOURCE_DIR / "plp-datasets.json"
    if plp_file.exists():
        try:
            with open(plp_file, 'r', encoding='utf-8') as f:
                products["plp"] = json.load(f)
            print(f"  ✅ Loaded {len(products['plp'])} PLP products")
        except Exception as e:
            print(f"  ⚠️  Error loading PLP data: {e}")
    
    # Load PIP datasets
    pip_file = SOURCE_DIR / "pip-datasets.json"
    if pip_file.exists():
        try:
            with open(pip_file, 'r', encoding='utf-8') as f:
                products["pip"] = json.load(f)
            print(f"  ✅ Loaded {len(products['pip'])} PIP products")
        except Exception as e:
            print(f"  ⚠️  Error loading PIP data: {e}")
    
    return products


def main():
    """Main execution function"""
    print("=" * 80)
    print("🍊 ORANGE CATALOG DATA TRANSFORMATION")
    print("=" * 80)
    
    # Step 1: Create directory structure
    create_directory_structure()
    
    # Step 2: Scan scraped categories
    categories = scan_scraped_categories()
    
    # Step 3: Build taxonomy
    taxonomy = build_category_taxonomy(categories)
    
    # Save taxonomy index
    taxonomy_file = PRODUCTION_DIR / "categories" / "index.json"
    save_json(taxonomy, taxonomy_file)
    print(f"\n💾 Saved taxonomy to: {taxonomy_file}")
    
    # Step 4: Load existing products
    products = load_existing_products()
    
    print("\n" + "=" * 80)
    print("✅ PHASE 1 COMPLETE - Directory structure and taxonomy created")
    print("=" * 80)
    print(f"\nNext steps:")
    print(f"  1. Extract category metadata from manifests")
    print(f"  2. Process and tag products with filter attributes")
    print(f"  3. Extract and organize images")
    print(f"  4. Generate navigation manifests")


if __name__ == "__main__":
    main()
