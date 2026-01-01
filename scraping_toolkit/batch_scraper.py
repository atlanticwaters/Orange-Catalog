#!/usr/bin/env python3
"""
Batch scraper - orchestrates PLP and PIP scraping
"""

import argparse
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
import config


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'='*70}")
    print(f"🚀 {description}")
    print(f"{'='*70}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        return False


def scrape_all_categories(output_dir: Path):
    """Scrape all PLP pages"""
    cmd = [
        'python3',
        'scrape_plp.py',
        '--output', str(output_dir)
    ]
    return run_command(cmd, "Scraping all category pages (PLPs)")


def scrape_category_products(category: str, output_dir: Path):
    """Scrape specific category"""
    cmd = [
        'python3',
        'scrape_plp.py',
        '--categories', category,
        '--output', str(output_dir)
    ]
    return run_command(cmd, f"Scraping category: {category}")


def scrape_products_from_plp(plp_dir: Path, output_dir: Path, limit: int = None):
    """Scrape PIPs for products found in PLP data"""
    # Collect all product IDs from PLP results
    product_ids = []
    
    for json_file in plp_dir.rglob("*_plp.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
                product_ids.extend(data.get('productIds', []))
        except:
            continue
    
    # Remove duplicates
    product_ids = list(dict.fromkeys(product_ids))
    
    print(f"\n📦 Found {len(product_ids)} unique products from PLP data")
    
    if limit:
        product_ids = product_ids[:limit]
        print(f"   Limiting to {limit} products")
    
    # Save to temp file
    temp_file = Path('/tmp/product_ids.json')
    with open(temp_file, 'w') as f:
        json.dump(product_ids, f)
    
    # Run PIP scraper
    cmd = [
        'python3',
        'scrape_pip.py',
        '--input-file', str(temp_file),
        '--output', str(output_dir)
    ]
    
    return run_command(cmd, f"Scraping {len(product_ids)} product detail pages (PIPs)")


def scrape_existing_product_ids(limit: int = None):
    """Scrape PIPs for product IDs already in production data"""
    cmd = [
        'python3',
        'scrape_pip.py',
    ]
    
    if limit:
        cmd.extend(['--limit', str(limit)])
    
    return run_command(cmd, "Scraping products from existing production data")


def main():
    parser = argparse.ArgumentParser(
        description='Batch scraper for Home Depot data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all priority categories
  python3 batch_scraper.py --all-categories
  
  # Scrape specific category
  python3 batch_scraper.py --category french-door
  
  # Scrape products from existing production data (first 100)
  python3 batch_scraper.py --existing-products --limit 100
  
  # Full workflow: scrape categories, then scrape top 50 products from each
  python3 batch_scraper.py --all-categories --scrape-products --limit 50
        """
    )
    
    parser.add_argument('--all-categories', action='store_true', 
                       help='Scrape all priority category PLPs')
    parser.add_argument('--category', type=str, 
                       help='Scrape specific category')
    parser.add_argument('--scrape-products', action='store_true',
                       help='After scraping PLPs, scrape the product PIPs')
    parser.add_argument('--existing-products', action='store_true',
                       help='Scrape PIPs for products already in production data')
    parser.add_argument('--limit', type=int,
                       help='Limit number of products to scrape')
    parser.add_argument('--output', type=str, default=str(config.OUTPUT_DIR),
                       help='Output directory')
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    plp_output = output_dir / "plp_data"
    pip_output = output_dir / "pip_data"
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = output_dir / f"session_{timestamp}"
    session_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*70}")
    print(f"🛠️  BATCH SCRAPER")
    print(f"{'='*70}")
    print(f"Session directory: {session_dir}\n")
    
    results = {
        'timestamp': timestamp,
        'success': [],
        'failed': []
    }
    
    # Scrape categories
    if args.all_categories:
        if scrape_all_categories(plp_output):
            results['success'].append('all_categories')
            
            # Optionally scrape products
            if args.scrape_products:
                time.sleep(2)
                if scrape_products_from_plp(plp_output, pip_output, args.limit):
                    results['success'].append('products_from_plp')
                else:
                    results['failed'].append('products_from_plp')
        else:
            results['failed'].append('all_categories')
    
    elif args.category:
        if scrape_category_products(args.category, plp_output):
            results['success'].append(f'category_{args.category}')
            
            if args.scrape_products:
                time.sleep(2)
                if scrape_products_from_plp(plp_output, pip_output, args.limit):
                    results['success'].append('products_from_category')
                else:
                    results['failed'].append('products_from_category')
        else:
            results['failed'].append(f'category_{args.category}')
    
    # Scrape existing products
    if args.existing_products:
        if scrape_existing_product_ids(args.limit):
            results['success'].append('existing_products')
        else:
            results['failed'].append('existing_products')
    
    # Save session results
    session_log = session_dir / "results.json"
    with open(session_log, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"✨ BATCH SCRAPING COMPLETE")
    print(f"{'='*70}")
    print(f"✅ Successful tasks: {len(results['success'])}")
    print(f"❌ Failed tasks: {len(results['failed'])}")
    print(f"\nSession log: {session_log}")
    
    if results['failed']:
        print(f"\nFailed tasks:")
        for task in results['failed']:
            print(f"  • {task}")


if __name__ == '__main__':
    main()
