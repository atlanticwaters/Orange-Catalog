# Extract Category Data - Complete Python Script

## Overview

This script extracts structured category data from scraped Home Depot HTML files and outputs JSON files for each category with product IDs, breadcrumbs, images, filters, and metadata.

## Installation

### Prerequisites
- Python 3.13+ (or 3.8+)
- Virtual environment (recommended)

### Setup

1. **Install dependencies:**
```bash
pip install beautifulsoup4 lxml
```

Or if using the project virtual environment:
```bash
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
pip install beautifulsoup4 lxml
```

## Usage

### Basic Usage

Run the extraction script:
```bash
python extract_category_data.py
```

This will:
1. Scan all HTML files in the scraped data directories
2. Extract category information and product data
3. Save JSON files to `production data/categories/`
4. Generate summary text files for quick inspection

### Analyzing Results

View statistics about extracted data:
```bash
python analyze_categories.py
```

### Searching Categories

Search for specific categories or products:
```bash
# Search by category name
python search_categories.py --name "dishwasher"

# Find which categories contain a product
python search_categories.py --product "311411352"

# Get a specific category by ID
python search_categories.py --id "appliances/dishwashers"

# List all categories
python search_categories.py --list-all

# Show statistics
python search_categories.py --stats
```

## Output Structure

### Directory Layout

```
production data/categories/
├── appliances/
│   ├── dishwashers.json
│   ├── dishwashers_summary.txt
│   ├── refrigerators/
│   │   ├── french-door.json
│   │   └── ...
│   └── ...
├── tools/
│   ├── drills.json
│   ├── power-drills.json
│   └── ...
├── appliances.json
├── tools.json
└── ...
```

### JSON Schema

Each category JSON file contains:

```json
{
  "categoryId": "appliances/dishwashers",
  "name": "Dishwashers",
  "originalUrl": "https://www.homedepot.com/...",
  "archiveTime": "2025-12-31T18:29:14.819Z",
  
  "breadcrumbs": [
    {"name": "Home", "url": "..."},
    {"name": "Appliances", "url": "..."}
  ],
  
  "filters": [
    {
      "filterGroupId": "brand",
      "filterGroupName": "Brand",
      "filterType": "checkbox",
      "options": [
        {"value": "ge", "label": "GE", "count": 42}
      ]
    }
  ],
  
  "quickFilters": [
    {"name": "French Door", "url": "...", "image": "...", "imageAlt": "..."}
  ],
  
  "featuredBrands": [
    {"name": "Samsung", "url": "...", "logo": "..."}
  ],
  
  "heroImage": "https://...",
  
  "productIds": ["311411352", "320243591", ...],
  "totalProducts": 42,
  
  "images": {
    "600px": [{"filename": "images/35.avif", "url": "https://..."}],
    "svgs": [{"filename": "images/logo.svg", "url": "https://..."}],
    "other": [...]
  },
  
  "metadata": {
    "title": "Dishwashers - The Home Depot",
    "categoryType": "PLP Landing Pages",
    "categoryFolder": "Dishwashers"
  }
}
```

## Features

### Data Extraction

✅ **Product IDs** - Extracted from multiple sources:
- Product page links (`/p/name/123456`)
- Data attributes (`data-product-id`, `data-itemid`)
- JSON-LD schemas (`<script type="application/ld+json">`)
- Component click tracking IDs

✅ **Breadcrumbs** - Navigation path from:
- HTML breadcrumb elements
- JSON-LD BreadcrumbList schemas

✅ **Images** - Categorized from manifest.json:
- 600-703px product images
- SVG logos and icons
- Other image assets

✅ **Category Metadata** - Including:
- Original URLs
- Archive timestamps
- Category hierarchy
- Page titles

### Current Limitations

⚠️ **Filters** - Most filter data is loaded dynamically
- Static HTML doesn't contain complete filter definitions
- Would require capturing API responses or JavaScript execution

⚠️ **Quick Filters** - Visual navigation components
- Often rendered client-side via React/JavaScript
- Not consistently present in static HTML

⚠️ **Featured Brands** - Brand sections
- May be in separate dynamic components
- Not all pages have featured brand sections

## Processing Statistics

### Latest Run Results
- **Categories Processed:** 86
- **Success Rate:** 100% (0 errors)
- **Unique Products Found:** 1,918
- **Total Images Catalogued:** 7,990
- **Processing Time:** ~6 seconds

### Category Breakdown
- **Top Level Pages:** 15 (Appliances, Tools, Bath, Kitchen, etc.)
- **Appliance Subcategories:** 23 (Dishwashers, Refrigerators, etc.)
- **Tool Subcategories:** 47 (Drills, Saws, Sanders, etc.)
- **Refrigerator Types:** 6 (French Door, Side-by-Side, etc.)

### Top Categories by Product Count
1. Ice Makers - 75 products
2. Mini Fridges - 69 products
3. Drill Bits - 62 products
4. Saw Blades - 58 products
5. Modular Tool Storage - 56 products

## Code Examples

### Load a Category

```python
import json
from pathlib import Path

# Load category data
with open('production data/categories/appliances/dishwashers.json') as f:
    category = json.load(f)

print(f"Category: {category['name']}")
print(f"Products: {category['totalProducts']}")
print(f"URL: {category['originalUrl']}")

# List products
for product_id in category['productIds']:
    print(f"  - Product {product_id}")
```

### Find All Products

```python
from pathlib import Path
import json

all_products = set()
categories_path = Path('production data/categories')

for json_file in categories_path.rglob('*.json'):
    if json_file.stem.endswith('_summary'):
        continue
    
    with open(json_file) as f:
        data = json.load(f)
        all_products.update(data.get('productIds', []))

print(f"Total unique products: {len(all_products)}")
```

### Build Category Tree

```python
from pathlib import Path
import json
from collections import defaultdict

hierarchy = defaultdict(list)

for json_file in Path('production data/categories').rglob('*.json'):
    if json_file.stem.endswith('_summary'):
        continue
    
    with open(json_file) as f:
        data = json.load(f)
        category_id = data['categoryId']
        
        if '/' in category_id:
            parent = category_id.split('/')[0]
            hierarchy[parent].append(data['name'])
        else:
            hierarchy['root'].append(data['name'])

# Print hierarchy
for parent, children in hierarchy.items():
    print(f"{parent}: {len(children)} subcategories")
```

## Technical Details

### Technologies
- **BeautifulSoup4** - HTML parsing and DOM traversal
- **lxml** - Fast XML/HTML parser backend
- **pathlib** - Modern file system operations
- **json** - Data serialization
- **re** - Regular expressions for pattern matching

### Architecture
- **Modular design** - Separate extraction methods for each data type
- **Error handling** - Graceful failure with detailed logging
- **Performance** - Parallel file processing where possible
- **Extensibility** - Easy to add new extraction patterns

### Extraction Strategies

1. **Multi-source Product IDs**
   - Regex on links: `/p/{name}/{id}`
   - DOM attributes: `data-product-id`, `data-itemid`
   - Structured data: JSON-LD schemas
   - Analytics: `clickid` tracking attributes

2. **Breadcrumb Detection**
   - Semantic HTML: `role="navigation"`, `aria-label="breadcrumb"`
   - CSS classes: `.breadcrumb`, `.breadcrumbs`
   - Structured data: BreadcrumbList schema

3. **Image Classification**
   - Size detection: URL parameters (`Resize=`, dimensions)
   - Format detection: File extensions (`.svg`, `.avif`, `.jpg`)
   - Purpose inference: Filename patterns

## Troubleshooting

### Common Issues

**Problem:** No products found in category
- Check if HTML contains product listings
- Verify product ID patterns match Home Depot format
- Look for dynamic loading indicators

**Problem:** Missing filters
- Filters are likely loaded via JavaScript/API
- Static HTML won't contain dynamic filter data
- Consider capturing network requests

**Problem:** Images not categorized correctly
- Check manifest.json file exists
- Verify image URL patterns
- Update classification logic in `extract_images()`

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

### Potential Enhancements

1. **Parse Individual Product Pages**
   - Extract full product details (name, price, specs)
   - Build product database
   - Link products to categories

2. **Capture Dynamic Filters**
   - Intercept API calls during page load
   - Parse filter response JSON
   - Build complete filter definitions

3. **Extract Product Attributes**
   - Parse specification tables
   - Extract ratings and reviews
   - Capture pricing and availability

4. **Build Search Index**
   - Full-text search across categories
   - Product lookup by attributes
   - Faceted navigation

5. **Generate Category Pages**
   - Create HTML pages from JSON data
   - Build static site generator
   - Add filtering and sorting

## Files Included

- `extract_category_data.py` - Main extraction script
- `analyze_categories.py` - Data analysis and statistics
- `search_categories.py` - Search and query tool
- `EXTRACTION_RESULTS.md` - Detailed results documentation
- `README_EXTRACT.md` - This file

## License & Attribution

This is a data extraction tool for archival and analysis purposes.
Source data from The Home Depot website.

---

**Last Updated:** December 31, 2025  
**Version:** 1.0.0
