#!/usr/bin/env python3
"""
Search and query tool for extracted category data.

Usage:
    python search_categories.py --name "dishwasher"
    python search_categories.py --product "311411352"
    python search_categories.py --list-all
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


class CategorySearch:
    """Search engine for category data."""
    
    def __init__(self, categories_path: Path):
        self.categories_path = categories_path
        self.categories = []
        self.load_all_categories()
    
    def load_all_categories(self):
        """Load all category JSON files."""
        for json_file in self.categories_path.rglob("*.json"):
            if json_file.stem.endswith('_summary'):
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_file_path'] = str(json_file)
                    self.categories.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    def search_by_name(self, query: str) -> List[Dict[str, Any]]:
        """Search categories by name."""
        query = query.lower()
        results = []
        
        for cat in self.categories:
            if query in cat.get('name', '').lower() or query in cat.get('categoryId', '').lower():
                results.append(cat)
        
        return results
    
    def search_by_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Find categories containing a specific product."""
        results = []
        
        for cat in self.categories:
            if product_id in cat.get('productIds', []):
                results.append(cat)
        
        return results
    
    def get_category_by_id(self, category_id: str) -> Dict[str, Any]:
        """Get a category by its ID."""
        for cat in self.categories:
            if cat.get('categoryId') == category_id:
                return cat
        return None
    
    def list_all_categories(self) -> List[Dict[str, str]]:
        """List all categories with basic info."""
        return [{
            'id': cat.get('categoryId', ''),
            'name': cat.get('name', ''),
            'products': cat.get('totalProducts', 0),
            'url': cat.get('originalUrl', '')
        } for cat in self.categories]
    
    def print_category_details(self, category: Dict[str, Any]):
        """Pretty print category details."""
        print("\n" + "="*70)
        print(f"Category: {category.get('name', 'Unknown')}")
        print("="*70)
        print(f"ID:               {category.get('categoryId', 'N/A')}")
        print(f"URL:              {category.get('originalUrl', 'N/A')}")
        print(f"Archive Time:     {category.get('archiveTime', 'N/A')}")
        print(f"Total Products:   {category.get('totalProducts', 0)}")
        
        # Breadcrumbs
        breadcrumbs = category.get('breadcrumbs', [])
        if breadcrumbs:
            print(f"Breadcrumbs:      {' > '.join([b['name'] for b in breadcrumbs])}")
        
        # Filters
        filters = category.get('filters', [])
        if filters:
            print(f"\nFilters ({len(filters)}):")
            for filt in filters:
                print(f"  • {filt['filterGroupName']} ({filt['filterType']})")
                print(f"    Options: {len(filt.get('options', []))}")
        
        # Quick filters
        quick_filters = category.get('quickFilters', [])
        if quick_filters:
            print(f"\nQuick Filters ({len(quick_filters)}):")
            for qf in quick_filters[:5]:
                print(f"  • {qf.get('name', 'N/A')}")
            if len(quick_filters) > 5:
                print(f"  ... and {len(quick_filters) - 5} more")
        
        # Featured brands
        brands = category.get('featuredBrands', [])
        if brands:
            print(f"\nFeatured Brands ({len(brands)}):")
            for brand in brands[:5]:
                print(f"  • {brand.get('name', 'N/A')}")
            if len(brands) > 5:
                print(f"  ... and {len(brands) - 5} more")
        
        # Hero image
        hero = category.get('heroImage')
        if hero:
            print(f"\nHero Image:       {hero}")
        
        # Images
        images = category.get('images', {})
        print(f"\nImages:")
        print(f"  600px:  {len(images.get('600px', []))}")
        print(f"  SVGs:   {len(images.get('svgs', []))}")
        print(f"  Other:  {len(images.get('other', []))}")
        
        # Product IDs
        product_ids = category.get('productIds', [])
        print(f"\nProduct IDs ({len(product_ids)}):")
        if product_ids:
            # Show first 10
            for pid in product_ids[:10]:
                print(f"  • {pid}")
            if len(product_ids) > 10:
                print(f"  ... and {len(product_ids) - 10} more")
        
        print("\nFile:", category.get('_file_path', 'N/A'))
        print("="*70)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description='Search category data')
    parser.add_argument('--name', help='Search by category name')
    parser.add_argument('--product', help='Search by product ID')
    parser.add_argument('--id', help='Get category by exact ID')
    parser.add_argument('--list-all', action='store_true', help='List all categories')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    
    args = parser.parse_args()
    
    # Initialize search
    categories_path = Path(__file__).parent / "production data" / "categories"
    search = CategorySearch(categories_path)
    
    print(f"\n📚 Loaded {len(search.categories)} categories\n")
    
    # Execute search
    if args.list_all:
        print("All Categories:")
        print("-" * 70)
        for cat in sorted(search.list_all_categories(), key=lambda x: x['id']):
            print(f"{cat['id']:<40} {cat['products']:>4} products")
    
    elif args.name:
        results = search.search_by_name(args.name)
        print(f"Found {len(results)} categories matching '{args.name}':\n")
        for cat in results:
            search.print_category_details(cat)
    
    elif args.product:
        results = search.search_by_product(args.product)
        print(f"Product {args.product} found in {len(results)} categories:\n")
        for cat in results:
            print(f"  • {cat.get('name')} ({cat.get('categoryId')})")
            print(f"    {cat.get('originalUrl')}")
            print()
    
    elif args.id:
        cat = search.get_category_by_id(args.id)
        if cat:
            search.print_category_details(cat)
        else:
            print(f"❌ Category '{args.id}' not found")
    
    elif args.stats:
        all_products = set()
        for cat in search.categories:
            all_products.update(cat.get('productIds', []))
        
        print("Statistics:")
        print("-" * 70)
        print(f"Total categories:     {len(search.categories)}")
        print(f"Total unique products: {len(all_products)}")
        print(f"Avg products/category: {len(all_products) / len(search.categories):.1f}")
        
        # Category with most products
        max_cat = max(search.categories, key=lambda x: x.get('totalProducts', 0))
        print(f"\nCategory with most products:")
        print(f"  {max_cat.get('name')} - {max_cat.get('totalProducts')} products")
        
        # Category types
        types = {}
        for cat in search.categories:
            cat_type = cat.get('metadata', {}).get('categoryType', 'Unknown')
            types[cat_type] = types.get(cat_type, 0) + 1
        
        print(f"\nCategories by type:")
        for cat_type, count in sorted(types.items()):
            print(f"  {cat_type}: {count}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
