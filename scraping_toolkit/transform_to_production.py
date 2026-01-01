#!/usr/bin/env python3
"""
Transform extracted product data into iOS-ready production structure
Follows the schema and structure defined in production data/README.md
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def categorize_product(product: dict) -> str:
    """Determine category path based on product data"""
    name = product.get('name', '').lower()
    brand = (product.get('brand') or '').lower()
    
    # Furniture - check first as it's a broad category
    if any(word in name for word in ['bed', 'mattress', 'nightstand', 'dresser', 'armoire', 'chest of drawers']):
        return 'furniture/bedroom'
    elif any(word in name for word in ['sofa', 'couch', 'sectional', 'loveseat', 'recliner', 'coffee table', 'end table', 'tv stand', 'entertainment center']):
        return 'furniture/living-room'
    elif any(word in name for word in ['desk', 'office chair', 'filing cabinet', 'bookshelf', 'bookcase']):
        return 'furniture/office'
    elif any(word in name for word in ['dining table', 'dining chair', 'bar stool', 'kitchen island']):
        return 'furniture/dining'
    elif 'furniture' in name:
        return 'furniture'
    
    # Garage storage and organization
    elif any(word in name for word in ['garage cabinet', 'garage storage', 'tool chest', 'tool cabinet', 'workbench', 'pegboard', 'wall organization', 'overhead storage']) or \
         ('garage' in name and ('cabinet' in name or 'storage' in name or 'shelf' in name)):
        return 'garage/storage'
    elif 'garage flooring' in name or ('garage' in name and 'floor' in name):
        return 'garage/flooring'
    elif 'garage door' in name:
        return 'garage/doors'
    
    # Artificial plants and home decor
    elif ('artificial' in name or 'faux' in name or 'nearly natural' in name) and ('plant' in name or 'tree' in name or 'flower' in name or 'vine' in name):
        if 'tree' in name:
            return 'home-decor/artificial-plants/trees'
        elif 'succulent' in name or 'topiary' in name:
            return 'home-decor/artificial-plants/specialty'
        else:
            return 'home-decor/artificial-plants'
    elif 'area rug' in name or ('rug' in name and 'ft' in name):
        return 'home-decor/rugs'
    elif 'curtain' in name or 'drape' in name or 'window treatment' in name:
        return 'home-decor/curtains'
    elif 'comforter' in name or 'duvet' in name or 'bedding' in name:
        return 'home-decor/bedding'
    elif 'wall art' in name or 'canvas' in name or 'painting' in name:
        return 'home-decor/wall-art'
    elif 'mirror' in name:
        return 'home-decor/mirrors'
    
    # Automotive
    elif any(word in name for word in ['battery charger', 'car charger', 'automotive battery']):
        return 'automotive/battery-chargers'
    elif ('jack' in name or 'lift' in name) and ('car' in name or 'vehicle' in name or 'automotive' in name or 'ton' in name):
        return 'automotive/jacks-lifts'
    elif 'motor oil' in name or 'transmission fluid' in name or 'brake fluid' in name:
        return 'automotive/fluids'
    elif 'car wash' in name or 'car wax' in name or 'automotive cleaning' in name:
        return 'automotive/cleaning'
    
    # Air compressors and pneumatic tools
    elif 'air compressor' in name or 'compressor' in name:
        if 'portable' in name:
            return 'tools/air-compressors/portable'
        elif 'stationary' in name:
            return 'tools/air-compressors/stationary'
        elif 'pancake' in name or 'hotdog' in name:
            return 'tools/air-compressors/portable'
        else:
            return 'tools/air-compressors'
    elif 'pneumatic' in name or 'air nailer' in name or 'air stapler' in name:
        if 'framing' in name:
            return 'tools/nailers/framing'
        elif 'finish' in name or 'brad' in name:
            return 'tools/nailers/finishing'
        elif 'roofing' in name:
            return 'tools/nailers/roofing'
        elif 'flooring' in name:
            return 'tools/nailers/flooring'
        else:
            return 'tools/nailers/pneumatic'
    
    # Electrical and smart home
    elif 'smart switch' in name or 'smart dimmer' in name or 'caseta' in name:
        return 'electrical/smart-home'
    elif 'outlet' in name or 'receptacle' in name or ('usb' in name and 'port' in name):
        return 'electrical/outlets'
    elif 'breaker' in name or 'circuit breaker' in name:
        return 'electrical/breakers'
    elif 'wire' in name or 'cable' in name or 'conduit' in name:
        return 'electrical/wire-cable'
    elif 'wall plate' in name or 'cover plate' in name:
        return 'electrical/wall-plates'
    elif 'surge protector' in name or 'power strip' in name:
        return 'electrical/surge-protection'
    elif 'lighting' in name or 'light bulb' in name:
        return 'electrical/lighting'
    
    # Storage and organization
    elif 'storage bin' in name or 'storage container' in name or 'tote' in name:
        return 'storage/bins-totes'
    elif 'shelving' in name or 'shelf' in name:
        return 'storage/shelving'
    elif 'zip tie' in name or 'cable tie' in name:
        return 'storage/organization'
    
    # Refrigerator categories
    elif 'refrigerator' in name or 'fridge' in name or 'freezer' in name:
        if 'french door' in name:
            return 'appliances/refrigerators/french-door'
        elif 'side by side' in name or 'side-by-side' in name:
            return 'appliances/refrigerators/side-by-side'
        elif 'bottom freezer' in name:
            return 'appliances/refrigerators/bottom-freezer'
        elif 'top freezer' in name:
            return 'appliances/refrigerators/top-freezer'
        elif 'mini' in name or 'compact' in name:
            return 'appliances/refrigerators/mini-fridges'
        elif 'counter depth' in name:
            return 'appliances/refrigerators/counter-depth'
        elif 'freezerless' in name or 'all refrigerator' in name:
            return 'appliances/refrigerators/freezerless'
        else:
            return 'appliances/refrigerators'
    
    # Other appliances
    elif 'dishwasher' in name:
        return 'appliances/dishwashers'
    elif 'range' in name and 'hood' not in name:
        return 'appliances/ranges'
    elif 'cooktop' in name:
        return 'appliances/cooktops'
    elif 'oven' in name and 'microwave' not in name:
        return 'appliances/wall-ovens'
    elif 'microwave' in name:
        return 'appliances/microwaves'
    elif 'range hood' in name or 'vent hood' in name:
        return 'appliances/range-hoods'
    elif 'washer' in name or 'dryer' in name or 'laundry' in name:
        return 'appliances/washers-dryers'
    elif 'air conditioner' in name or 'ac unit' in name:
        return 'appliances/air-conditioners'
    elif 'ice maker' in name:
        return 'appliances/ice-makers'
    elif 'beverage' in name and 'cooler' in name:
        return 'appliances/beverage-coolers'
    elif 'garbage disposal' in name:
        return 'appliances/garbage-disposals'
    elif 'vacuum' in name:
        return 'appliances/floor-care'
    elif 'fan' in name:
        return 'appliances/fans'
    
    # Power tools
    elif 'drill' in name:
        if 'hammer' in name or 'rotary' in name:
            return 'tools/drills/hammer-drills'
        elif 'impact driver' in name:
            return 'tools/drills/impact-drivers'
        elif 'drill press' in name:
            return 'tools/drills/drill-presses'
        elif 'angle' in name:
            return 'tools/drills/angle-drills'
        else:
            return 'tools/drills'
    elif 'saw' in name:
        if 'miter' in name:
            return 'tools/saws/miter-saws'
        elif 'circular' in name:
            return 'tools/saws/circular-saws'
        elif 'table' in name:
            return 'tools/saws/table-saws'
        elif 'jigsaw' in name or 'jig saw' in name:
            return 'tools/saws/jigsaws'
        elif 'reciprocating' in name or 'sawzall' in name:
            return 'tools/saws/reciprocating-saws'
        elif 'band' in name:
            return 'tools/saws/band-saws'
        else:
            return 'tools/saws'
    elif 'sander' in name:
        return 'tools/sanders'
    elif 'grinder' in name:
        return 'tools/grinders'
    elif 'router' in name and 'wood' in name:
        return 'tools/routers'
    elif 'planer' in name:
        return 'tools/planers'
    elif 'impact wrench' in name:
        return 'tools/impact-wrenches'
    elif 'nailer' in name or 'nail gun' in name:
        return 'tools/nailers'
    elif 'battery' in name and ('volt' in name or 'ah' in name):
        return 'tools/batteries'
    elif 'combo kit' in name or 'tool kit' in name:
        return 'tools/combo-kits'
    
    # Default to general tools or appliances
    elif any(word in name for word in ['tool', 'power']):
        return 'tools'
    elif any(word in name for word in ['appliance', 'kitchen']):
        return 'appliances'
    else:
        return 'other'


def transform_to_product_detail(product: dict) -> dict:
    """Transform extracted product to production detail structure"""
    item_id = product['itemId']
    
    # Build pricing structure
    pricing = {
        'currentPrice': float(product.get('price', 0)) if product.get('price') else None,
        'currency': product.get('currency', 'USD')
    }
    
    # Build rating structure
    rating_data = product.get('rating')
    rating = None
    if rating_data:
        rating = {
            'average': rating_data.get('average', 0),
            'count': rating_data.get('count', 0)
        }
    
    # Build brand structure
    brand_name = product.get('brand') or 'Unknown'
    brand = {
        'name': brand_name,
        'logoUrl': f"images/brands/{slugify(brand_name)}.svg" if brand_name != 'Unknown' else None
    }
    
    # Build media structure
    image_url = product.get('imageUrl', '')
    media = {
        'primaryImage': image_url,
        'images': [
            {
                'url': image_url,
                'altText': product.get('name', ''),
                'type': 'primary'
            }
        ] if image_url else []
    }
    
    # Build availability
    availability = {
        'inStock': product.get('inStock', True),
        'availableForPickup': True,
        'availableForDelivery': True
    }
    
    return {
        'productId': item_id,
        'identifiers': {
            'internetNumber': item_id,
            'modelNumber': '',  # Not available in JSON-LD
            'storeSkuNumber': item_id
        },
        'brand': brand,
        'title': product.get('name', ''),
        'shortDescription': product.get('description', ''),
        'longDescription': product.get('description', ''),
        'pricing': pricing,
        'rating': rating,
        'media': media,
        'availability': availability,
        'badges': [],
        'specifications': {},
        'shipping': {
            'freeShipping': pricing.get('currentPrice', 0) >= 45 if pricing.get('currentPrice') else False
        },
        'version': '1.0',
        'lastUpdated': datetime.now().isoformat()
    }


def transform_to_category_product(product: dict) -> dict:
    """Transform to simplified category product listing"""
    price = product.get('price')
    rating_data = product.get('rating')
    
    product_data = {
        'productId': product['itemId'],
        'modelNumber': '',
        'brand': product.get('brand') or 'Unknown',
        'title': product.get('name', ''),
        'rating': {
            'average': rating_data.get('average', 0),
            'count': rating_data.get('count', 0)
        } if rating_data else None,
        'images': {
            'primary': product.get('imageUrl', '')
        },
        'badges': [],
        'availability': {
            'inStock': product.get('inStock', True)
        }
    }
    
    if price is not None:
        product_data['price'] = {
            'current': float(price),
            'currency': product.get('currency', 'USD')
        }
    
    return product_data


def main():
    base_dir = Path(__file__).parent.parent
    source_file = base_dir / '_source data' / 'pip-datasets.json'
    output_dir = base_dir / 'production data'
    
    print(f"\n{'='*70}")
    print(f"🔄 Transforming Data to iOS Production Structure")
    print(f"{'='*70}\n")
    
    # Load extracted product data
    print("📂 Loading extracted product data...")
    with open(source_file) as f:
        products_dict = json.load(f)
    
    products = list(products_dict.values())
    print(f"   ✅ Loaded {len(products)} products")
    
    # Organize by category
    print("\n📁 Organizing products by category...")
    categories = defaultdict(list)
    
    for product in products:
        category_path = categorize_product(product)
        categories[category_path].append(product)
    
    print(f"   ✅ Organized into {len(categories)} categories")
    
    # Create product detail files
    print("\n💾 Creating product detail files...")
    products_dir = output_dir / 'products'
    created_count = 0
    
    for product in products:
        product_id = product['itemId']
        product_dir = products_dir / product_id
        product_dir.mkdir(parents=True, exist_ok=True)
        
        detail_file = product_dir / 'details.json'
        product_detail = transform_to_product_detail(product)
        
        with open(detail_file, 'w') as f:
            json.dump(product_detail, f, indent=2)
        
        created_count += 1
        if created_count % 100 == 0:
            print(f"   Created {created_count}/{len(products)} product files...")
    
    print(f"   ✅ Created {created_count} product detail files")
    
    # Create category files
    print("\n📦 Creating category files...")
    categories_dir = output_dir / 'categories'
    category_count = 0
    
    for category_path, category_products in sorted(categories.items()):
        # Create category directory structure
        parts = category_path.split('/')
        cat_file_dir = categories_dir / '/'.join(parts[:-1]) if len(parts) > 1 else categories_dir
        cat_file_dir.mkdir(parents=True, exist_ok=True)
        
        # Create category file
        category_file = cat_file_dir / f"{parts[-1]}.json"
        
        # Build breadcrumbs
        breadcrumbs = [{'label': 'Home', 'url': '/'}]
        for i, part in enumerate(parts):
            label = part.replace('-', ' ').title()
            url = '/' + '/'.join(parts[:i+1])
            breadcrumbs.append({'label': label, 'url': url})
        
        # Get unique brands
        brands = {}
        for p in category_products:
            brand = p.get('brand') or 'Unknown'
            if brand not in brands:
                brands[brand] = {
                    'brandId': slugify(brand),
                    'brandName': brand,
                    'logoUrl': f"images/brands/{slugify(brand)}.svg",
                    'count': 0
                }
            brands[brand]['count'] += 1
        
        category_data = {
            'categoryId': category_path,
            'name': parts[-1].replace('-', ' ').title(),
            'slug': parts[-1],
            'path': f"/categories/{category_path}",
            'version': '1.0',
            'lastUpdated': datetime.now().isoformat(),
            'breadcrumbs': breadcrumbs,
            'pageInfo': {
                'totalResults': len(category_products)
            },
            'featuredBrands': sorted(
                list(brands.values()),
                key=lambda x: x['count'],
                reverse=True
            )[:10],
            'products': [transform_to_category_product(p) for p in category_products]
        }
        
        with open(category_file, 'w') as f:
            json.dump(category_data, f, indent=2)
        
        category_count += 1
        print(f"   Created {category_path} ({len(category_products)} products)")
    
    print(f"\n   ✅ Created {category_count} category files")
    
    # Create category index
    print("\n📑 Creating category index...")
    index_data = {
        'version': '1.0',
        'lastUpdated': datetime.now().isoformat(),
        'totalCategories': category_count,
        'totalProducts': len(products),
        'categories': []
    }
    
    # Build hierarchical structure
    hierarchy = defaultdict(lambda: defaultdict(list))
    
    for category_path in sorted(categories.keys()):
        parts = category_path.split('/')
        if len(parts) == 1:
            dept = parts[0]
            hierarchy[dept]['_count'] = hierarchy[dept].get('_count', 0) + len(categories[category_path])
        elif len(parts) >= 2:
            dept = parts[0]
            subcat = '/'.join(parts[1:])
            hierarchy[dept][subcat] = len(categories[category_path])
            hierarchy[dept]['_count'] = hierarchy[dept].get('_count', 0) + len(categories[category_path])
    
    for dept, subcats in sorted(hierarchy.items()):
        dept_count = subcats.pop('_count', 0)
        dept_data = {
            'id': dept,
            'name': dept.replace('-', ' ').title(),
            'slug': dept,
            'productCount': dept_count,
            'subcategories': []
        }
        
        for subcat, count in sorted(subcats.items()):
            subcat_parts = subcat.split('/')
            dept_data['subcategories'].append({
                'id': f"{dept}/{subcat}",
                'name': subcat_parts[-1].replace('-', ' ').title(),
                'slug': subcat_parts[-1],
                'productCount': count,
                'path': f"/categories/{dept}/{subcat}"
            })
        
        index_data['categories'].append(dept_data)
    
    index_file = categories_dir / 'index.json'
    with open(index_file, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"   ✅ Created category index")
    
    # Update SUMMARY.json
    print("\n📊 Updating SUMMARY.json...")
    
    # Get brand stats
    brand_stats = defaultdict(int)
    for product in products:
        brand = product.get('brand') or 'Unknown'
        brand_stats[brand] += 1
    
    summary = {
        'version': '1.0',
        'generatedAt': datetime.now().isoformat(),
        'dataStats': {
            'totalCategories': category_count,
            'totalProducts': len(products),
            'totalBrands': len(brand_stats),
            'categoriesWithProducts': category_count
        },
        'topBrands': [
            {'name': brand, 'productCount': count}
            for brand, count in sorted(brand_stats.items(), key=lambda x: x[1], reverse=True)[:20]
        ],
        'departments': [
            {
                'name': dept['name'],
                'slug': dept['slug'],
                'categoryCount': len(dept['subcategories']),
                'productCount': dept['productCount']
            }
            for dept in index_data['categories']
        ]
    }
    
    summary_file = output_dir / 'SUMMARY.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"   ✅ Updated SUMMARY.json")
    
    # Final summary
    print(f"\n{'='*70}")
    print(f"✨ Transformation Complete!")
    print(f"{'='*70}")
    print(f"   Products: {len(products)}")
    print(f"   Categories: {category_count}")
    print(f"   Brands: {len(brand_stats)}")
    print(f"\n   Output: {output_dir}")
    print(f"\n📱 iOS-Ready Structure:")
    print(f"   ✅ categories/index.json - Master navigation")
    print(f"   ✅ categories/[dept]/[category].json - Category listings")
    print(f"   ✅ products/[id]/details.json - Product details")
    print(f"   ✅ SUMMARY.json - Global stats")
    
    print(f"\n🔝 Top Categories:")
    for cat_path, prods in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"   {cat_path}: {len(prods)} products")


if __name__ == '__main__':
    main()
