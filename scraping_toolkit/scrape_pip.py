#!/usr/bin/env python3
"""
Scrape Product Info Pages (PIPs) from Home Depot
Extracts: full product details, specs, pricing, reviews, images
"""

import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from tenacity import retry, stop_after_attempt, wait_exponential
import config


class PIPScraper:
    """Scrapes Product Info Pages from Home Depot"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def scrape_pip(self, product_id: str) -> Optional[Dict]:
        """Scrape a single product page"""
        url = f"{config.HD_BASE_URL}/p/{product_id}"
        
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract product data
            data = {
                'productId': product_id,
                'url': url,
                'scrapedAt': datetime.now().isoformat(),
                'name': self._extract_name(soup),
                'brand': self._extract_brand(soup),
                'model': self._extract_model(soup),
                'price': self._extract_price(soup),
                'rating': self._extract_rating(soup),
                'reviewCount': self._extract_review_count(soup),
                'images': self._extract_images(soup),
                'description': self._extract_description(soup),
                'specifications': self._extract_specifications(soup),
                'features': self._extract_features(soup),
                'dimensions': self._extract_dimensions(soup),
                'inStock': self._extract_stock_status(soup),
                'categories': self._extract_categories(soup),
            }
            
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"   ❌ Product {product_id} not found (404)")
                return None
            raise
        except Exception as e:
            print(f"   ❌ Error scraping {product_id}: {str(e)}")
            raise
    
    def _extract_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product name"""
        # Try multiple selectors
        selectors = [
            ('h1', {'class': lambda x: x and 'product' in x.lower()}),
            ('h1', {}),
            ('meta', {'property': 'og:title'}),
        ]
        
        for tag, attrs in selectors:
            elem = soup.find(tag, attrs)
            if elem:
                if tag == 'meta':
                    return elem.get('content', '').strip()
                return elem.get_text(strip=True)
        
        return None
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand name"""
        # Check meta tags
        brand_meta = soup.find('meta', {'property': 'product:brand'})
        if brand_meta:
            return brand_meta.get('content', '').strip()
        
        # Check structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'brand' in data:
                    brand = data['brand']
                    if isinstance(brand, dict):
                        return brand.get('name', '')
                    return str(brand)
            except:
                continue
        
        return None
    
    def _extract_model(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract model number"""
        # Look for model number in specs or text
        model_elem = soup.find(text=lambda x: x and 'model' in x.lower())
        if model_elem:
            # Try to extract model number after "Model:"
            import re
            match = re.search(r'model[:\s]+([A-Z0-9\-]+)', model_elem, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract pricing information"""
        price_data = {}
        
        # Look for price elements
        price_elem = soup.find('div', {'data-component': 'price'})
        if not price_elem:
            price_elem = soup.find(class_=lambda x: x and 'price' in x.lower())
        
        if price_elem:
            # Try to find dollar amount
            import re
            price_text = price_elem.get_text()
            match = re.search(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', price_text)
            if match:
                price_data['value'] = float(match.group(1).replace(',', ''))
                price_data['currency'] = 'USD'
        
        # Check for sale/original price
        original = soup.find(class_=lambda x: x and ('original' in str(x).lower() or 'was' in str(x).lower()))
        if original:
            import re
            match = re.search(r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)', original.get_text())
            if match:
                price_data['originalValue'] = float(match.group(1).replace(',', ''))
        
        return price_data if price_data else None
    
    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product rating"""
        # Check structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'aggregateRating' in data:
                    return float(data['aggregateRating'].get('ratingValue', 0))
            except:
                continue
        
        # Look for rating in HTML
        rating_elem = soup.find(attrs={'aria-label': lambda x: x and 'rating' in x.lower()})
        if rating_elem:
            import re
            match = re.search(r'(\d+\.?\d*)', rating_elem.get('aria-label', ''))
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract number of reviews"""
        # Look for review count
        review_elem = soup.find(text=lambda x: x and 'review' in x.lower())
        if review_elem:
            import re
            match = re.search(r'(\d+(?:,\d{3})*)\s*review', review_elem, re.IGNORECASE)
            if match:
                return int(match.group(1).replace(',', ''))
        
        return None
    
    def _extract_images(self, soup: BeautifulSoup) -> List[str]:
        """Extract product images"""
        images = []
        
        # Method 1: Check image gallery
        gallery = soup.find('div', {'data-component': lambda x: x and 'media' in str(x).lower()})
        if gallery:
            for img in gallery.find_all('img'):
                src = img.get('src', '')
                if src and src not in images:
                    # Prefer higher resolution
                    if '600' not in src and '1000' not in src:
                        src = src.replace('300', '600')
                    images.append(src)
        
        # Method 2: Check all images with product context
        for img in soup.find_all('img', src=True):
            src = img['src']
            if 'product' in src.lower() or 'images' in src:
                if src not in images:
                    images.append(src)
        
        # Limit to reasonable number
        return images[:20]
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product description"""
        # Look for description section
        desc_elem = soup.find('div', {'data-component': 'description'})
        if not desc_elem:
            desc_elem = soup.find(class_=lambda x: x and 'description' in str(x).lower())
        
        if desc_elem:
            return desc_elem.get_text(strip=True)
        
        # Try meta description
        meta = soup.find('meta', {'name': 'description'})
        if meta:
            return meta.get('content', '').strip()
        
        return None
    
    def _extract_specifications(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract product specifications"""
        specs = []
        
        # Look for specs table
        spec_section = soup.find('table', class_=lambda x: x and 'spec' in str(x).lower())
        if spec_section:
            for row in spec_section.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    specs.append({
                        'name': cells[0].get_text(strip=True),
                        'value': cells[1].get_text(strip=True)
                    })
        
        # Alternative: Look for dl (definition list)
        spec_dl = soup.find('dl', class_=lambda x: x and 'spec' in str(x).lower())
        if spec_dl:
            terms = spec_dl.find_all('dt')
            definitions = spec_dl.find_all('dd')
            for term, definition in zip(terms, definitions):
                specs.append({
                    'name': term.get_text(strip=True),
                    'value': definition.get_text(strip=True)
                })
        
        return specs
    
    def _extract_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract product features/highlights"""
        features = []
        
        # Look for features list
        features_section = soup.find(['ul', 'div'], class_=lambda x: x and ('feature' in str(x).lower() or 'highlight' in str(x).lower()))
        if features_section:
            for li in features_section.find_all('li'):
                feature = li.get_text(strip=True)
                if feature:
                    features.append(feature)
        
        return features
    
    def _extract_dimensions(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract product dimensions"""
        dimensions = {}
        
        # Look for dimension specifications
        for spec_elem in soup.find_all(text=lambda x: x and any(dim in x.lower() for dim in ['width', 'height', 'depth', 'weight'])):
            import re
            # Try to extract dimensions
            if 'width' in spec_elem.lower():
                match = re.search(r'width[:\s]+(\d+\.?\d*)\s*in', spec_elem, re.IGNORECASE)
                if match:
                    dimensions['width'] = float(match.group(1))
            
            if 'height' in spec_elem.lower():
                match = re.search(r'height[:\s]+(\d+\.?\d*)\s*in', spec_elem, re.IGNORECASE)
                if match:
                    dimensions['height'] = float(match.group(1))
            
            if 'depth' in spec_elem.lower():
                match = re.search(r'depth[:\s]+(\d+\.?\d*)\s*in', spec_elem, re.IGNORECASE)
                if match:
                    dimensions['depth'] = float(match.group(1))
        
        return dimensions if dimensions else None
    
    def _extract_stock_status(self, soup: BeautifulSoup) -> bool:
        """Extract stock availability"""
        # Look for "Add to Cart" button
        add_to_cart = soup.find('button', text=lambda x: x and 'add to cart' in x.lower())
        if add_to_cart and not add_to_cart.get('disabled'):
            return True
        
        # Check for out of stock message
        out_of_stock = soup.find(text=lambda x: x and 'out of stock' in x.lower())
        if out_of_stock:
            return False
        
        return True  # Assume in stock if we can't determine
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """Extract category breadcrumbs"""
        categories = []
        
        breadcrumb_nav = soup.find('nav', attrs={'aria-label': lambda x: x and 'breadcrumb' in str(x).lower()})
        if breadcrumb_nav:
            for link in breadcrumb_nav.find_all('a'):
                cat = link.get_text(strip=True)
                if cat and cat.lower() != 'home':
                    categories.append(cat)
        
        return categories
    
    def save_result(self, data: Dict, output_dir: Path):
        """Save scraped product data"""
        product_id = data['productId']
        product_dir = output_dir / product_id
        product_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as details.json (compatible with existing format)
        json_file = product_dir / "details.json"
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Scrape Home Depot Product Info Pages')
    parser.add_argument('--product-ids', nargs='+', help='Specific product IDs to scrape')
    parser.add_argument('--input-file', type=str, help='JSON file containing product IDs')
    parser.add_argument('--limit', type=int, help='Limit number of products to scrape')
    parser.add_argument('--output', type=str, default=str(config.OUTPUT_DIR / "products"), help='Output directory')
    
    args = parser.parse_args()
    
    # Collect product IDs
    product_ids = []
    
    if args.product_ids:
        product_ids = args.product_ids
    elif args.input_file:
        # Load from JSON file
        with open(args.input_file) as f:
            data = json.load(f)
            if isinstance(data, list):
                product_ids = data
            elif isinstance(data, dict) and 'productIds' in data:
                product_ids = data['productIds']
    else:
        # Load from existing production data
        prod_data_dir = config.BASE_DIR / "production data" / "categories"
        for json_file in prod_data_dir.rglob("*.json"):
            if json_file.name == "index.json":
                continue
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    product_ids.extend(data.get('productIds', []))
            except:
                continue
    
    # Remove duplicates and apply limit
    product_ids = list(dict.fromkeys(product_ids))
    if args.limit:
        product_ids = product_ids[:args.limit]
    
    if not product_ids:
        print("❌ No product IDs to scrape. Use --product-ids or --input-file")
        return
    
    print(f"\n📋 Scraping {len(product_ids)} products...")
    
    # Initialize scraper
    scraper = PIPScraper()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Scrape products
    success = 0
    failed = 0
    
    for product_id in tqdm(product_ids, desc="Scraping products"):
        try:
            data = scraper.scrape_pip(product_id)
            if data:
                scraper.save_result(data, output_dir)
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ Failed to scrape {product_id}: {e}")
            failed += 1
        
        # Rate limiting
        time.sleep(config.RATE_LIMIT_DELAY)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"✨ Scraping Complete!")
    print(f"   Success: {success}")
    print(f"   Failed: {failed}")
    print(f"   Output directory: {output_dir}")


if __name__ == '__main__':
    main()
