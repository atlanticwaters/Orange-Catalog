#!/usr/bin/env python3
"""
Generate lightweight offline catalog metadata for iOS app.
Creates a minimal dataset for offline browsing without full product details.
"""

import json
from pathlib import Path
from datetime import datetime

def generate_offline_catalog():
    """Generate offline catalog metadata."""
    
    base_dir = Path(__file__).parent / "production data"
    categories_dir = base_dir / "categories"
    
    print("Generating offline catalog...")
    
    offline_catalog = {
        "version": "1.0.0",
        "generatedAt": datetime.now().isoformat(),
        "categories": [],
        "quickAccess": {
            "topBrands": [],
            "popularCategories": [],
            "recentlyViewed": []
        },
        "metadata": {
            "totalProducts": 0,
            "totalCategories": 0,
            "downloadSize": "5 MB"
        }
    }
    
    # Load category index
    with open(categories_dir / "index.json", 'r', encoding='utf-8') as f:
        category_index = json.load(f)
    
    offline_catalog["metadata"]["totalCategories"] = len(category_index.get("categories", []))
    
    total_products = 0
    
    # Process each category
    for category_info in category_index.get("categories", []):
        category_id = category_info.get("id")
        category_file = categories_dir / f"{category_id}.json"
        
        if not category_file.exists():
            continue
        
        with open(category_file, 'r', encoding='utf-8') as f:
            category_data = json.load(f)
        
        # Create lightweight category entry
        category_entry = {
            "id": category_id,
            "name": category_data.get("category_name", ""),
            "productCount": category_data.get("total_products", 0),
            "topProducts": []
        }
        
        # Include top 10 products with minimal data
        products = category_data.get("products", [])[:10]
        for product in products:
            category_entry["topProducts"].append({
                "id": product.get("product_id", ""),
                "name": product.get("name", ""),
                "brand": product.get("brand", ""),
                "price": product.get("price"),
                "rating": product.get("rating"),
                "imageUrl": product.get("image_url", "")
            })
        
        offline_catalog["categories"].append(category_entry)
        total_products += len(category_data.get("products", []))
    
    offline_catalog["metadata"]["totalProducts"] = total_products
    
    # Load summary for popular data
    summary_file = base_dir / "SUMMARY.json"
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        # Add top brands
        offline_catalog["quickAccess"]["topBrands"] = [
            {
                "name": brand.get("name", ""),
                "productCount": brand.get("productCount", 0)
            }
            for brand in summary.get("topBrands", [])[:10]
        ]
    
    # Sort categories by product count
    offline_catalog["categories"].sort(key=lambda x: x["productCount"], reverse=True)
    offline_catalog["quickAccess"]["popularCategories"] = [
        {
            "id": cat["id"],
            "name": cat["name"],
            "productCount": cat["productCount"]
        }
        for cat in offline_catalog["categories"][:8]
    ]
    
    # Save offline catalog
    output_file = base_dir / "offline-catalog.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(offline_catalog, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Offline catalog generated: {output_file}")
    print(f"  - Categories: {len(offline_catalog['categories'])}")
    print(f"  - Total products: {total_products}")
    print(f"  - Top products per category: 10")
    
    # Calculate size
    import os
    size_mb = os.path.getsize(output_file) / 1024 / 1024
    print(f"  - File size: {size_mb:.2f} MB")

if __name__ == "__main__":
    generate_offline_catalog()
