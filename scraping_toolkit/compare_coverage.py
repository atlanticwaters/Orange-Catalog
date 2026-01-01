#!/usr/bin/env python3
"""
Compare newly extracted product IDs with existing product detail data
Shows what needs to be scraped for full product information
"""

import json
from pathlib import Path
from collections import defaultdict


def load_extracted_product_ids(plp_data_dir: Path) -> dict:
    """Load all product IDs from extracted PLP data"""
    all_ids = set()
    category_breakdown = {}
    
    # Load from batch summary if available
    summary_file = plp_data_dir / 'batch_processing_summary.json'
    if summary_file.exists():
        with open(summary_file) as f:
            summary = json.load(f)
            for cat in summary['categories']:
                slug = cat['slug']
                ids = set(cat['productIds'])
                category_breakdown[slug] = {
                    'name': cat['category'],
                    'productIds': ids,
                    'count': len(ids)
                }
                all_ids.update(ids)
    
    return all_ids, category_breakdown


def load_existing_product_details(source_data_dir: Path) -> set:
    """Load product IDs that already have full details"""
    existing_ids = set()
    
    # Check pip-datasets.json
    pip_file = source_data_dir / 'pip-datasets.json'
    if pip_file.exists():
        with open(pip_file) as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if 'itemId' in item:
                        existing_ids.add(str(item['itemId']))
            elif isinstance(data, dict):
                for key, item in data.items():
                    if isinstance(item, dict) and 'itemId' in item:
                        existing_ids.add(str(item['itemId']))
                    elif isinstance(key, str) and key.isdigit():
                        existing_ids.add(key)
    
    return existing_ids


def main():
    base_dir = Path(__file__).parent.parent
    plp_data_dir = base_dir / '_scraped data' / 'Automated Scrapes' / 'plp_data'
    source_data_dir = base_dir / '_source data'
    
    print(f"\n{'='*70}")
    print(f"📊 Product Data Comparison Report")
    print(f"{'='*70}\n")
    
    # Load data
    print("🔍 Loading extracted product IDs...")
    extracted_ids, category_breakdown = load_extracted_product_ids(plp_data_dir)
    print(f"   ✅ Found {len(extracted_ids)} unique product IDs across {len(category_breakdown)} categories")
    
    print("\n🔍 Loading existing product details...")
    existing_ids = load_existing_product_details(source_data_dir)
    print(f"   ✅ Found {len(existing_ids)} products with full details")
    
    # Calculate what we need
    need_details = extracted_ids - existing_ids
    already_have = extracted_ids & existing_ids
    
    print(f"\n{'='*70}")
    print(f"📈 Summary")
    print(f"{'='*70}")
    print(f"   Total product IDs extracted:     {len(extracted_ids):,}")
    print(f"   Already have full details:       {len(already_have):,} ({len(already_have)/len(extracted_ids)*100:.1f}%)")
    print(f"   Need to scrape details:          {len(need_details):,} ({len(need_details)/len(extracted_ids)*100:.1f}%)")
    
    # Category breakdown
    print(f"\n📦 Category Breakdown:")
    print(f"{'='*70}")
    
    by_parent = defaultdict(lambda: {'categories': [], 'total': 0, 'need': 0, 'have': 0})
    
    for slug, cat_data in sorted(category_breakdown.items(), key=lambda x: x[1]['count'], reverse=True):
        cat_ids = cat_data['productIds']
        cat_need = cat_ids - existing_ids
        cat_have = cat_ids & existing_ids
        
        # Determine parent category
        if 'refrigerator' in slug or 'fridge' in slug or 'freezer' in slug:
            parent = 'Refrigerators & Freezers'
        elif any(kw in slug for kw in ['dishwasher', 'range', 'oven', 'cooktop', 'microwave', 
                                         'hood', 'disposal', 'ice_maker', 'beverage', 'appliance']):
            parent = 'Major Appliances'
        elif any(kw in slug for kw in ['drill', 'saw', 'sander', 'grinder', 'hammer', 'impact', 
                                         'router', 'planer', 'wrench', 'driver']):
            parent = 'Power Tools'
        elif 'tool' in slug:
            parent = 'Tool Accessories & Storage'
        else:
            parent = 'Other'
        
        by_parent[parent]['categories'].append({
            'name': cat_data['name'],
            'slug': slug,
            'total': len(cat_ids),
            'need': len(cat_need),
            'have': len(cat_have)
        })
        by_parent[parent]['total'] += len(cat_ids)
        by_parent[parent]['need'] += len(cat_need)
        by_parent[parent]['have'] += len(cat_have)
    
    for parent in sorted(by_parent.keys()):
        stats = by_parent[parent]
        print(f"\n{parent}:")
        print(f"   {len(stats['categories'])} categories | {stats['total']} products | Need: {stats['need']} | Have: {stats['have']}")
        
        # Show top categories that need scraping
        need_sorted = sorted(stats['categories'], key=lambda x: x['need'], reverse=True)[:5]
        for cat in need_sorted:
            if cat['need'] > 0:
                pct = (cat['need'] / cat['total']) * 100 if cat['total'] > 0 else 0
                print(f"      • {cat['name']}: {cat['need']}/{cat['total']} need scraping ({pct:.0f}%)")
    
    # Save detailed report
    report = {
        'summary': {
            'totalExtracted': len(extracted_ids),
            'alreadyHaveDetails': len(already_have),
            'needToScrape': len(need_details),
            'coveragePercent': (len(already_have) / len(extracted_ids) * 100) if extracted_ids else 0
        },
        'categoryBreakdown': dict(by_parent),
        'productIdsNeedingScrape': sorted(list(need_details))
    }
    
    report_file = plp_data_dir / 'coverage_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"💾 Detailed report saved to: {report_file.relative_to(base_dir)}")
    
    print(f"\n{'='*70}")
    print(f"🚀 Next Steps:")
    print(f"{'='*70}")
    
    if len(need_details) > 0:
        print(f"\n   To scrape full details for {len(need_details):,} products:")
        print(f"   python3 scraping_toolkit/scrape_pip.py --batch")
    else:
        print(f"\n   ✅ You already have details for all products!")
        print(f"   Run the transformation pipeline to generate production data:")
        print(f"   python3 extract_category_data.py")
        print(f"   python3 finalize_production_data.py")


if __name__ == '__main__':
    main()
