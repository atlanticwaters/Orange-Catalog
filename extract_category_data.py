#!/usr/bin/env python3
"""
Extract category data from scraped Home Depot HTML files.

This script parses HTML files from the scraped data directories and extracts:
- Product listings
- Filter definitions
- Quick filters with images
- Featured brands
- Hero/banner images
- Breadcrumb navigation
- Category metadata

Output is saved as JSON files in the production data/categories structure.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CategoryExtractor:
    """Extract category data from Home Depot HTML files."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.scraped_data_path = base_path / "_scraped data" / "THD Product Page Data"
        self.output_path = base_path / "production data" / "categories"
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Category directories to process
        self.category_dirs = [
            "Top Level THD Pages",
            "PLP Landing Pages",
            "Tool Categories",
            "Fridge PLP/Fridge PLP Items"
        ]
    
    def process_all_categories(self):
        """Process all category directories."""
        total_processed = 0
        total_errors = 0
        
        for category_type in self.category_dirs:
            category_path = self.scraped_data_path / category_type
            
            if not category_path.exists():
                logger.warning(f"Category path not found: {category_path}")
                continue
            
            logger.info(f"Processing category type: {category_type}")
            
            # Find all subdirectories with index.html
            for category_dir in category_path.iterdir():
                if not category_dir.is_dir():
                    continue
                
                html_file = category_dir / "index.html"
                manifest_file = category_dir / "manifest.json"
                
                if not html_file.exists():
                    logger.debug(f"No index.html found in {category_dir.name}")
                    continue
                
                try:
                    logger.info(f"Processing: {category_dir.name}")
                    category_data = self.extract_category_data(
                        html_file, 
                        manifest_file,
                        category_type,
                        category_dir.name
                    )
                    
                    if category_data:
                        self.save_category_data(category_data, category_type, category_dir.name)
                        total_processed += 1
                        logger.info(f"✓ Successfully processed {category_dir.name}")
                    
                except Exception as e:
                    total_errors += 1
                    logger.error(f"✗ Error processing {category_dir.name}: {str(e)}", exc_info=True)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing complete!")
        logger.info(f"Successfully processed: {total_processed}")
        logger.info(f"Errors: {total_errors}")
        logger.info(f"{'='*60}")
    
    def extract_category_data(
        self, 
        html_file: Path, 
        manifest_file: Path,
        category_type: str,
        category_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract data from a single category."""
        
        # Read HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Read manifest if exists
        manifest = {}
        if manifest_file.exists():
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
        
        # Extract data
        category_data = {
            "categoryId": self.generate_category_id(category_type, category_name),
            "name": self.extract_category_name(soup, manifest, category_name),
            "originalUrl": manifest.get("originalUrl", ""),
            "archiveTime": manifest.get("archiveTime", ""),
            "breadcrumbs": self.extract_breadcrumbs(soup),
            "filters": self.extract_filters(soup),
            "quickFilters": self.extract_quick_filters(soup),
            "featuredBrands": self.extract_featured_brands(soup),
            "heroImage": self.extract_hero_image(soup, manifest),
            "productIds": self.extract_product_ids(soup),
            "totalProducts": 0,
            "images": self.extract_images(manifest),
            "metadata": {
                "title": manifest.get("title", ""),
                "categoryType": category_type,
                "categoryFolder": category_name
            }
        }
        
        category_data["totalProducts"] = len(category_data["productIds"])
        
        return category_data
    
    def generate_category_id(self, category_type: str, category_name: str) -> str:
        """Generate a category ID from the type and name."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        clean_name = re.sub(r'[^\w\s-]', '', category_name.lower())
        clean_name = re.sub(r'[-\s]+', '-', clean_name).strip('-')
        
        # Map category types to parent categories
        type_map = {
            "Top Level THD Pages": "",
            "PLP Landing Pages": "appliances",
            "Tool Categories": "tools",
            "Fridge PLP/Fridge PLP Items": "appliances/refrigerators"
        }
        
        parent = type_map.get(category_type, "")
        
        if parent:
            return f"{parent}/{clean_name}"
        return clean_name
    
    def extract_category_name(self, soup: BeautifulSoup, manifest: Dict, fallback: str) -> str:
        """Extract the category name from the page."""
        # Try page title first
        title = manifest.get("title", "")
        if title:
            # Remove "- The Home Depot" suffix
            title = re.sub(r'\s*-\s*The Home Depot.*$', '', title, flags=re.IGNORECASE)
            if title:
                return title.strip()
        
        # Try H1 headings
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Fallback to directory name
        return fallback.replace('-', ' ').title()
    
    def extract_breadcrumbs(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract breadcrumb navigation."""
        breadcrumbs = []
        
        # Look for breadcrumb containers
        breadcrumb_patterns = [
            {'role': 'navigation', 'aria-label': re.compile(r'breadcrumb', re.I)},
            {'class': re.compile(r'breadcrumb', re.I)},
            {'id': re.compile(r'breadcrumb', re.I)}
        ]
        
        for pattern in breadcrumb_patterns:
            container = soup.find(attrs=pattern)
            if container:
                # Find all links in breadcrumb
                links = container.find_all('a')
                for link in links:
                    breadcrumbs.append({
                        "name": link.get_text(strip=True),
                        "url": link.get('href', '')
                    })
                break
        
        # Also check for JSON-LD breadcrumb schema
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'BreadcrumbList':
                    for item in data.get('itemListElement', []):
                        breadcrumbs.append({
                            "name": item.get('name', ''),
                            "url": item.get('item', '')
                        })
                    break
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return breadcrumbs
    
    def extract_filters(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract filter definitions from the page."""
        filters = []
        
        # Look for filter sections - common patterns
        filter_containers = soup.find_all(attrs={
            'class': re.compile(r'filter|facet|refinement', re.I)
        })
        
        for container in filter_containers:
            # Look for filter groups
            filter_group = self.parse_filter_group(container)
            if filter_group:
                filters.append(filter_group)
        
        # Also check data attributes that might contain filter info
        filter_data_elements = soup.find_all(attrs={
            'data-component': re.compile(r'filter|facet', re.I)
        })
        
        for element in filter_data_elements:
            filter_group = self.parse_filter_group(element)
            if filter_group and filter_group not in filters:
                filters.append(filter_group)
        
        return filters
    
    def parse_filter_group(self, element) -> Optional[Dict[str, Any]]:
        """Parse a filter group element."""
        # Try to extract filter name/label
        label = element.find(['h2', 'h3', 'h4', 'label', 'legend'])
        if not label:
            return None
        
        filter_name = label.get_text(strip=True)
        if not filter_name:
            return None
        
        # Determine filter type
        filter_type = "checkbox"  # default
        if element.find('input', type='radio'):
            filter_type = "radio"
        elif element.find('select'):
            filter_type = "select"
        elif element.find(attrs={'type': 'range'}):
            filter_type = "range"
        
        # Extract options
        options = []
        
        # Checkbox/radio options
        inputs = element.find_all('input', type=['checkbox', 'radio'])
        for inp in inputs:
            label_text = ""
            # Find associated label
            label_elem = element.find('label', {'for': inp.get('id')})
            if label_elem:
                label_text = label_elem.get_text(strip=True)
            elif inp.parent and inp.parent.name == 'label':
                label_text = inp.parent.get_text(strip=True)
            
            if label_text:
                options.append({
                    "value": inp.get('value', ''),
                    "label": label_text,
                    "count": self.extract_count_from_text(label_text)
                })
        
        # Select options
        select = element.find('select')
        if select:
            for option in select.find_all('option'):
                option_text = option.get_text(strip=True)
                if option_text:
                    options.append({
                        "value": option.get('value', ''),
                        "label": option_text,
                        "count": self.extract_count_from_text(option_text)
                    })
        
        if not options:
            return None
        
        return {
            "filterGroupId": self.slugify(filter_name),
            "filterGroupName": filter_name,
            "filterType": filter_type,
            "options": options
        }
    
    def extract_count_from_text(self, text: str) -> Optional[int]:
        """Extract count from text like 'Brand Name (123)'."""
        match = re.search(r'\((\d+)\)', text)
        if match:
            return int(match.group(1))
        return None
    
    def slugify(self, text: str) -> str:
        """Convert text to slug format."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text.strip('-')
    
    def extract_quick_filters(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract quick filters with images."""
        quick_filters = []
        
        # Look for quick filter containers
        quick_filter_containers = soup.find_all(attrs={
            'class': re.compile(r'quick.?filter|visual.?nav', re.I),
            'data-component': re.compile(r'visual|quick', re.I)
        })
        
        for container in quick_filter_containers:
            # Find all links/buttons with images
            items = container.find_all(['a', 'button'])
            for item in items:
                img = item.find('img')
                if img:
                    quick_filters.append({
                        "name": item.get_text(strip=True) or img.get('alt', ''),
                        "url": item.get('href', ''),
                        "image": img.get('src', ''),
                        "imageAlt": img.get('alt', '')
                    })
        
        return quick_filters
    
    def extract_featured_brands(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract featured brands with logos."""
        brands = []
        
        # Look for brand sections
        brand_containers = soup.find_all(attrs={
            'class': re.compile(r'brand|manufacturer', re.I),
            'data-component': re.compile(r'brand', re.I)
        })
        
        for container in brand_containers:
            # Find brand links with images/logos
            brand_items = container.find_all('a')
            for item in brand_items:
                img = item.find('img')
                if img:
                    brands.append({
                        "name": img.get('alt', '') or item.get_text(strip=True),
                        "url": item.get('href', ''),
                        "logo": img.get('src', '')
                    })
        
        return brands
    
    def extract_hero_image(self, soup: BeautifulSoup, manifest: Dict) -> Optional[str]:
        """Extract hero/banner image."""
        # Look for hero images
        hero_patterns = [
            {'class': re.compile(r'hero|banner', re.I)},
            {'data-component': re.compile(r'hero|banner', re.I)}
        ]
        
        for pattern in hero_patterns:
            container = soup.find(attrs=pattern)
            if container:
                img = container.find('img')
                if img:
                    return img.get('src', '')
        
        # Check manifest for large images
        resources = manifest.get('resources', {})
        for key, url in resources.items():
            if 'hero' in key.lower() or 'banner' in key.lower():
                return url
        
        return None
    
    def extract_product_ids(self, soup: BeautifulSoup) -> List[str]:
        """Extract product IDs from the page."""
        product_ids = set()
        
        # Method 1: Look for product links in href
        product_links = soup.find_all('a', href=re.compile(r'/p/[^/]+/(\d+)'))
        for link in product_links:
            match = re.search(r'/p/[^/]+/(\d+)', link['href'])
            if match:
                product_ids.add(match.group(1))
        
        # Method 2: Look for data attributes
        product_elements = soup.find_all(attrs={
            'data-product-id': True,
            'data-itemid': True,
            'data-sku': True
        })
        
        for elem in product_elements:
            pid = elem.get('data-product-id') or elem.get('data-itemid') or elem.get('data-sku')
            if pid and pid.isdigit():
                product_ids.add(pid)
        
        # Method 3: Look in JSON-LD product schemas
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check for Product type
                    if data.get('@type') == 'Product':
                        sku = data.get('sku', '')
                        if sku and sku.isdigit():
                            product_ids.add(sku)
                    # Check for ItemList
                    elif data.get('@type') == 'ItemList':
                        for item in data.get('itemListElement', []):
                            if isinstance(item, dict):
                                sku = item.get('sku', '')
                                if sku and sku.isdigit():
                                    product_ids.add(sku)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Method 4: Look for clickid attributes (Home Depot specific)
        clickid_elements = soup.find_all(attrs={'clickid': re.compile(r'RelatedProducts')})
        for elem in clickid_elements:
            # Product IDs often in clickid value
            clickid = elem.get('clickid', '')
            numbers = re.findall(r'\d{9}', clickid)  # Home Depot product IDs are typically 9 digits
            product_ids.update(numbers)
        
        return sorted(list(product_ids))
    
    def extract_images(self, manifest: Dict) -> Dict[str, List[str]]:
        """Extract and categorize images from manifest."""
        images = {
            "600px": [],
            "svgs": [],
            "other": []
        }
        
        resources = manifest.get('resources', {})
        
        for filename, url in resources.items():
            if not filename.startswith('images/'):
                continue
            
            # Check for SVGs
            if filename.endswith('.svg') or url.endswith('.svg'):
                images['svgs'].append({
                    "filename": filename,
                    "url": url
                })
            # Check for 600px images (look for im=Resize in URL)
            elif '600' in url or '703' in url or 'Resize' in url:
                images['600px'].append({
                    "filename": filename,
                    "url": url
                })
            else:
                images['other'].append({
                    "filename": filename,
                    "url": url
                })
        
        return images
    
    def save_category_data(self, data: Dict, category_type: str, category_name: str):
        """Save category data to JSON file."""
        # Create category-specific output path
        category_id = data.get('categoryId', '')
        
        # Ensure output directory exists
        if '/' in category_id:
            parts = category_id.split('/')
            output_dir = self.output_path / '/'.join(parts[:-1])
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{parts[-1]}.json"
        else:
            output_file = self.output_path / f"{category_id}.json"
        
        # Save JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Saved: {output_file}")
        
        # Also save a summary for inspection
        summary_file = output_file.parent / f"{output_file.stem}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Category: {data['name']}\n")
            f.write(f"ID: {data['categoryId']}\n")
            f.write(f"URL: {data['originalUrl']}\n")
            f.write(f"Total Products: {data['totalProducts']}\n")
            f.write(f"Product IDs: {', '.join(data['productIds'][:10])}")
            if len(data['productIds']) > 10:
                f.write(f"... and {len(data['productIds']) - 10} more")
            f.write(f"\n\nFilters: {len(data['filters'])}\n")
            for filt in data['filters']:
                f.write(f"  - {filt['filterGroupName']} ({filt['filterType']}): {len(filt['options'])} options\n")
            f.write(f"\nQuick Filters: {len(data['quickFilters'])}\n")
            f.write(f"Featured Brands: {len(data['featuredBrands'])}\n")
            f.write(f"Breadcrumbs: {len(data['breadcrumbs'])}\n")


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Home Depot Category Data Extractor")
    logger.info("=" * 60)
    
    # Get base path
    base_path = Path(__file__).parent
    logger.info(f"Base path: {base_path}")
    
    # Create extractor
    extractor = CategoryExtractor(base_path)
    
    # Process all categories
    extractor.process_all_categories()
    
    logger.info("\nDone! Check the 'production data/categories' folder for output.")


if __name__ == "__main__":
    main()
