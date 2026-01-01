#!/usr/bin/env python3
"""
Generate search index for iOS app integration.
Creates a searchable index of all products with optimized data structure.
"""

import json
import os
from pathlib import Path
from datetime import datetime
import re

def normalize_text(text):
    """Normalize text for search indexing."""
    if not text:
        return ""
    # Convert to lowercase and remove special characters
    text = text.lower()
    text = re.sub(r'[^\w\s-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_keywords(text):
    """Extract keywords from text."""
    normalized = normalize_text(text)
    words = normalized.split()
    # Filter out common words and short words
    stop_words = {'the', 'and', 'or', 'for', 'with', 'in', 'on', 'at', 'to', 'a', 'an'}
    keywords = [w for w in words if len(w) > 2 and w not in stop_words]
    return list(set(keywords))

def generate_search_index():
    """Generate comprehensive search index."""
    
    base_dir = Path(__file__).parent / "production data"
    categories_dir = base_dir / "categories"
    products_dir = base_dir / "products"
    
    print("Generating search index...")
    
    search_index = {
        "version": "1.0.0",
        "generatedAt": datetime.now().isoformat(),
        "totalProducts": 0,
        "totalKeywords": 0,
        "products": [],
        "keywords": {},
        "categories": {},
        "brands": {}
    }
    
    # Load all categories
    category_files = list(categories_dir.glob("*.json"))
    category_files = [f for f in category_files if f.name != "index.json"]
    
    product_count = 0
    all_keywords = set()
    
    for category_file in category_files:
        print(f"Processing {category_file.name}...")
        
        with open(category_file, 'r', encoding='utf-8') as f:
            category_data = json.load(f)
        
        category_name = category_data.get('category_name', '')
        
        for product in category_data.get('products', []):
            product_id = product.get('product_id', '')
            if not product_id:
                continue
            
            # Extract searchable data
            name = product.get('name', '')
            brand = product.get('brand', '')
            price = product.get('price')
            rating = product.get('rating')
            
            # Generate keywords
            keywords = set()
            keywords.update(extract_keywords(name))
            keywords.update(extract_keywords(brand))
            keywords.update(extract_keywords(category_name))
            
            # Create search entry
            search_entry = {
                "id": product_id,
                "name": name,
                "brand": brand,
                "category": category_name,
                "price": price,
                "rating": rating,
                "keywords": sorted(list(keywords)),
                "imageUrl": product.get('image_url', '')
            }
            
            search_index["products"].append(search_entry)
            
            # Build keyword index (maps keyword to product IDs)
            for keyword in keywords:
                if keyword not in search_index["keywords"]:
                    search_index["keywords"][keyword] = []
                search_index["keywords"][keyword].append(product_id)
                all_keywords.add(keyword)
            
            # Build category index
            if category_name not in search_index["categories"]:
                search_index["categories"][category_name] = []
            search_index["categories"][category_name].append(product_id)
            
            # Build brand index
            if brand:
                if brand not in search_index["brands"]:
                    search_index["brands"][brand] = []
                search_index["brands"][brand].append(product_id)
            
            product_count += 1
            if product_count % 100 == 0:
                print(f"  Indexed {product_count} products...")
    
    search_index["totalProducts"] = product_count
    search_index["totalKeywords"] = len(all_keywords)
    
    # Sort products by name for binary search
    search_index["products"].sort(key=lambda x: x["name"].lower())
    
    # Save search index
    output_file = base_dir / "search-index.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Search index generated: {output_file}")
    print(f"  - Total products: {product_count}")
    print(f"  - Total keywords: {len(all_keywords)}")
    print(f"  - Total categories: {len(search_index['categories'])}")
    print(f"  - Total brands: {len(search_index['brands'])}")
    
    # Generate compact version for mobile
    compact_index = {
        "version": search_index["version"],
        "generatedAt": search_index["generatedAt"],
        "totalProducts": search_index["totalProducts"],
        "keywords": {k: v for k, v in search_index["keywords"].items() if len(v) >= 2},
        "categories": list(search_index["categories"].keys()),
        "brands": list(search_index["brands"].keys())
    }
    
    compact_file = base_dir / "search-index-compact.json"
    with open(compact_file, 'w', encoding='utf-8') as f:
        json.dump(compact_index, f, separators=(',', ':'), ensure_ascii=False)
    
    print(f"✓ Compact index generated: {compact_file}")
    
    # Calculate file sizes
    full_size = os.path.getsize(output_file) / 1024 / 1024
    compact_size = os.path.getsize(compact_file) / 1024 / 1024
    
    print(f"  - Full index size: {full_size:.2f} MB")
    print(f"  - Compact index size: {compact_size:.2f} MB")
    print(f"  - Size reduction: {((1 - compact_size/full_size) * 100):.1f}%")

if __name__ == "__main__":
    generate_search_index()
