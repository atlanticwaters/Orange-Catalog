# Category Data Extraction Results

## Overview
Successfully extracted category data from 86 HTML files in the scraped Home Depot data.

**Script:** `extract_category_data.py`  
**Run Date:** December 31, 2025  
**Status:** ✅ Complete (0 errors)

---

## Processing Summary

### Categories Processed by Type

1. **Top Level THD Pages** (15 categories)
   - Appliances, Bath, Building Materials, Cleaning, Electrical
   - Flooring, Garage, Garden Center, Home Decor, Kitchen
   - Lighting, Plumbing, Storage & Organization, Tools, Window Treatments

2. **PLP Landing Pages** (17 appliance categories)
   - Air Conditioners, Appliance Parts, Beverage Coolers, Cooktops
   - Dishwashers, Fans, Floor Care & Vacuums, Freezers
   - Garbage Disposals, Ice Makers, Microwaves, Mini Fridges
   - Range Hoods, Ranges, Small Kitchen Appliances, Wall Ovens
   - Washers & Dryers

3. **Tool Categories** (48 tool categories)
   - Power tools (drills, saws, grinders, sanders, etc.)
   - Hand tools, tool storage, modular systems
   - Accessories (batteries, drill bits, saw blades, etc.)
   - Specialty tools (welding, automotive, concrete, etc.)

4. **Fridge PLP Items** (6 refrigerator types)
   - French Door, Side by Side, Top Freezer, Bottom Freezer
   - Freezerless, Mini Fridges

---

## Output Structure

All extracted data is saved in: `production data/categories/`

### File Organization
```
categories/
├── {category-id}.json          # Main category data
├── {category-id}_summary.txt   # Human-readable summary
├── appliances/
│   ├── dishwashers.json
│   ├── dishwashers_summary.txt
│   ├── microwaves.json
│   ├── mini-fridges.json
│   └── ... (17 appliance subcategories)
├── tools/
│   ├── power-tools.json
│   ├── drills.json
│   ├── saws.json
│   └── ... (48 tool subcategories)
└── ... (15 top-level categories)
```

---

## Data Extracted Per Category

Each JSON file contains:

### 1. **Basic Information**
- `categoryId` - Unique identifier (e.g., "appliances/dishwashers")
- `name` - Display name
- `originalUrl` - Source URL from Home Depot
- `archiveTime` - When the page was scraped

### 2. **Navigation**
- `breadcrumbs[]` - Navigation path with names and URLs

### 3. **Products**
- `productIds[]` - Array of product SKUs found on the page
- `totalProducts` - Count of products

### 4. **Filters** (when available)
- `filters[]` - Filter groups with:
  - Filter name and ID
  - Filter type (checkbox, radio, select, range)
  - Options with values, labels, and counts

### 5. **Visual Elements**
- `quickFilters[]` - Quick filter tiles with images
- `featuredBrands[]` - Brand logos and links
- `heroImage` - Main banner/hero image URL

### 6. **Images**
- `images.600px[]` - Product/category images (600-703px)
- `images.svgs[]` - Vector logos and icons
- `images.other[]` - Other image assets

### 7. **Metadata**
- Original page title
- Category type classification
- Source folder name

---

## Sample Data

### Example: Dishwashers Category

```json
{
  "categoryId": "appliances/dishwashers",
  "name": "Dishwashers",
  "originalUrl": "https://www.homedepot.com/b/Appliances-Dishwashers/N-5yc1vZc3po",
  "totalProducts": 7,
  "productIds": [
    "206147639",
    "314298606",
    "322003405",
    "325602597",
    "329241860",
    "330817229",
    "336625538"
  ],
  "breadcrumbs": [
    {"name": "Home", "url": "https://www.homedepot.com/"},
    {"name": "Appliances", "url": "https://www.homedepot.com/b/Appliances/N-5yc1vZbv1w"}
  ],
  "images": {
    "600px": [...],
    "svgs": [...],
    "other": [...]
  }
}
```

### Example: Power Tool Combo Kits

```json
{
  "categoryId": "tools/power-tool-combo-kits",
  "name": "Power Tool Combo Kits",
  "totalProducts": 48,
  "breadcrumbs": [
    {"name": "Home", "url": "https://www.homedepot.com/"},
    {"name": "Tools", "url": "https://www.homedepot.com/b/Tools/N-5yc1vZc1xy"},
    {"name": "Power Tools", "url": "..."},
    {"name": "Power Tool Combo Kits", "url": "..."}
  ]
}
```

---

## Statistics

### Product Coverage
- **Total unique product IDs extracted:** ~2,500+
- **Categories with 40+ products:** Power Tool Combo Kits (48), Mini Fridges (60+)
- **Categories with breadcrumbs:** 86/86 (100%)
- **Categories with images:** 86/86 (100%)

### Data Quality
- ✅ All HTML files successfully parsed
- ✅ All manifest.json files cross-referenced
- ✅ Product IDs extracted from multiple sources:
  - Product page links
  - Data attributes
  - JSON-LD schemas
  - Component click IDs

---

## Notes & Limitations

### What Was Successfully Extracted
- ✅ Product IDs from visible HTML
- ✅ Breadcrumb navigation
- ✅ Hero/banner images
- ✅ Image manifests with URLs
- ✅ Page metadata and URLs

### Known Limitations
1. **Filters** - Most filter data is loaded dynamically via JavaScript/React
   - Static HTML doesn't contain filter definitions
   - Would need to capture API responses or wait for JS execution

2. **Quick Filters** - Similar to filters, often rendered client-side
   - Visual navigation components not in static HTML

3. **Featured Brands** - Brand logos may be in separate components
   - Not consistently present in static page structure

4. **Product Details** - Only IDs extracted, not full product information
   - Product names, prices, specs would require parsing individual product pages

### Future Enhancements
- Parse individual product detail pages
- Capture dynamic filter data from API calls
- Extract product specifications and attributes
- Build relationships between categories and products

---

## How to Use the Data

### Load Category Data
```python
import json
from pathlib import Path

# Load a category
with open('production data/categories/appliances/dishwashers.json') as f:
    dishwashers = json.load(f)

print(f"Found {dishwashers['totalProducts']} dishwashers")
for product_id in dishwashers['productIds']:
    print(f"  - Product {product_id}")
```

### Find All Product IDs
```python
from pathlib import Path
import json

all_products = set()
category_path = Path('production data/categories')

for json_file in category_path.rglob('*.json'):
    if json_file.stem.endswith('_summary'):
        continue
    with open(json_file) as f:
        data = json.load(f)
        all_products.update(data.get('productIds', []))

print(f"Total unique products across all categories: {len(all_products)}")
```

### Build Category Hierarchy
```python
from pathlib import Path
import json

hierarchy = {}
for json_file in Path('production data/categories').rglob('*.json'):
    if json_file.stem.endswith('_summary'):
        continue
    with open(json_file) as f:
        data = json.load(f)
        category_id = data['categoryId']
        parts = category_id.split('/')
        
        # Build nested structure
        current = hierarchy
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
```

---

## Script Details

### Technologies Used
- **Python 3.13**
- **BeautifulSoup4** - HTML parsing
- **lxml** - Fast XML/HTML parser
- **pathlib** - File system operations
- **json** - Data serialization
- **re** - Pattern matching

### Key Features
- Parallel processing of multiple category directories
- Graceful error handling with detailed logging
- Cross-referencing HTML with manifest.json
- Multiple extraction strategies for product IDs
- Automatic directory structure creation
- Human-readable summary files

### Performance
- **Processing time:** ~6 seconds
- **Success rate:** 100% (86/86 categories)
- **Error rate:** 0%

---

## Contact & Support

For questions about the extraction process or data structure:
- Check the summary files (`*_summary.txt`) for quick category overview
- Review the JSON files for complete data structure
- Examine the script source code (`extract_category_data.py`) for implementation details

---

**Last Updated:** December 31, 2025
