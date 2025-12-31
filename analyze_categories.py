#!/usr/bin/env python3
"""
Example usage of the extracted category data.

This script demonstrates how to work with the extracted category JSON files.
"""

import json
from pathlib import Path
from collections import defaultdict


def main():
    """Demonstrate various ways to use the extracted data."""
    
    categories_path = Path(__file__).parent / "production data" / "categories"
    
    print("=" * 70)
    print("Category Data Analysis")
    print("=" * 70)
    print()
    
    # 1. Count all categories
    all_categories = list(categories_path.rglob("*.json"))
    all_categories = [c for c in all_categories if not c.stem.endswith('_summary')]
    print(f"📊 Total categories extracted: {len(all_categories)}")
    print()
    
    # 2. Collect all product IDs
    all_products = set()
    category_product_counts = []
    
    for json_file in all_categories:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            products = data.get('productIds', [])
            all_products.update(products)
            
            category_product_counts.append({
                'name': data.get('name', json_file.stem),
                'id': data.get('categoryId', ''),
                'count': len(products)
            })
    
    print(f"🔢 Total unique products: {len(all_products)}")
    print()
    
    # 3. Show top categories by product count
    print("🏆 Top 10 Categories by Product Count:")
    print("-" * 70)
    top_categories = sorted(category_product_counts, key=lambda x: x['count'], reverse=True)[:10]
    for i, cat in enumerate(top_categories, 1):
        print(f"{i:2}. {cat['name']:<40} {cat['count']:>4} products")
    print()
    
    # 4. Category hierarchy
    print("📁 Category Hierarchy:")
    print("-" * 70)
    hierarchy = defaultdict(list)
    
    for json_file in all_categories:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            category_id = data.get('categoryId', '')
            name = data.get('name', '')
            
            if '/' in category_id:
                parent = category_id.split('/')[0]
                hierarchy[parent].append(name)
            else:
                hierarchy['root'].append(name)
    
    for parent, children in sorted(hierarchy.items()):
        if parent == 'root':
            print(f"\n📦 Top Level Categories ({len(children)}):")
            for child in sorted(children):
                print(f"   • {child}")
        else:
            print(f"\n📦 {parent.upper()} ({len(children)} subcategories):")
            for child in sorted(children)[:5]:
                print(f"   • {child}")
            if len(children) > 5:
                print(f"   ... and {len(children) - 5} more")
    print()
    
    # 5. Categories with breadcrumbs
    breadcrumb_stats = defaultdict(int)
    
    for json_file in all_categories:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            breadcrumbs = data.get('breadcrumbs', [])
            breadcrumb_stats[len(breadcrumbs)] += 1
    
    print("🔗 Breadcrumb Depth Distribution:")
    print("-" * 70)
    for depth in sorted(breadcrumb_stats.keys()):
        count = breadcrumb_stats[depth]
        bar = '█' * (count // 2)
        print(f"Depth {depth}: {count:3} categories {bar}")
    print()
    
    # 6. Image statistics
    total_600px = 0
    total_svgs = 0
    total_other = 0
    
    for json_file in all_categories:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            images = data.get('images', {})
            total_600px += len(images.get('600px', []))
            total_svgs += len(images.get('svgs', []))
            total_other += len(images.get('other', []))
    
    print("🖼️  Image Asset Summary:")
    print("-" * 70)
    print(f"600px images:  {total_600px:4}")
    print(f"SVG files:     {total_svgs:4}")
    print(f"Other images:  {total_other:4}")
    print(f"Total:         {total_600px + total_svgs + total_other:4}")
    print()
    
    # 7. Sample category details
    print("📄 Sample Category: Dishwashers")
    print("-" * 70)
    dishwashers_file = categories_path / "appliances" / "dishwashers.json"
    if dishwashers_file.exists():
        with open(dishwashers_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"Name:          {data.get('name')}")
            print(f"ID:            {data.get('categoryId')}")
            print(f"URL:           {data.get('originalUrl')}")
            print(f"Products:      {data.get('totalProducts')}")
            print(f"Breadcrumbs:   {' > '.join([b['name'] for b in data.get('breadcrumbs', [])])}")
            print(f"Product IDs:   {', '.join(data.get('productIds', [])[:5])}")
            if len(data.get('productIds', [])) > 5:
                print(f"               ... and {len(data.get('productIds', [])) - 5} more")
    print()
    
    print("=" * 70)
    print("✅ Analysis complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
