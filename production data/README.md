# Orange Catalog - Production Data Guide

**Generated:** December 31, 2025  
**Version:** 1.0  
**Total Size:** 11 MB

## 📊 Data Summary

- **88 Categories** across 15 departments
- **30 Product Details** with full specifications  
- **539 Images** (600px + SVG logos)
  - 175 product images
  - 185 brand logos
  - 11 UI elements
  - 168 hero/banner images

## 🗂️ Directory Structure

```
production data/
├── categories/
│   ├── index.json                      # Master navigation tree
│   ├── appliances/
│   │   ├── dishwashers.json
│   │   ├── mini-fridges.json
│   │   ├── refrigerators/
│   │   │   ├── french-door.json
│   │   │   ├── side-by-side.json
│   │   │   └── ...
│   │   └── ...
│   ├── tools/
│   │   ├── drills.json
│   │   ├── impact-drivers.json
│   │   └── ...
│   └── outdoors/
│       └── outdoor-power-equipment/
│           └── lawn-mowers.json
├── products/
│   └── [productId]/
│       └── details.json                # Full PIP data
├── images/
│   ├── products/                       # 600px product images
│   ├── brands/                         # SVG brand logos
│   ├── ui/                            # Badges, icons
│   └── heroes/                         # Hero/banner images
├── brands/
│   └── [brand info files]
└── SUMMARY.json
```

## 📦 Category JSON Structure

Each category file contains:

```json
{
  "categoryId": "appliances/refrigerators/french-door",
  "name": "French Door Refrigerators",
  "slug": "french-door",
  "path": "/categories/appliances/refrigerators/french-door",
  "version": "1.0",
  "lastUpdated": "2025-12-31",
  
  "breadcrumbs": [
    {"label": "Home", "url": "/"},
    {"label": "Appliances", "url": "/b/Appliances/N-5yc1vZbv1w"},
    {"label": "Refrigerators", "url": "/b/Appliances-Refrigerators/N-5yc1vZc3pi"},
    {"label": "French Door", "url": "/b/.../N-5yc1vZc3oo"}
  ],
  
  "pageInfo": {
    "totalResults": 289,
    "heroImage": {...},
    "seoDescription": "..."
  },
  
  "featuredBrands": [
    {
      "brandId": "GE",
      "brandName": "GE",
      "logoUrl": "https://images.thdstatic.com/catalog/brandLogos/ge-logo.svg",
      "filterUrl": "/b/.../GE/N-..."
    }
  ],
  
  "quickFilters": [
    {
      "filterId": "counter-depth",
      "label": "Counter Depth",
      "imageUrl": "...",
      "filterUrl": "..."
    }
  ],
  
  "filters": [
    {
      "filterGroupId": "brand",
      "filterGroupName": "Brand",
      "filterType": "checkbox",
      "options": [
        {
          "optionId": "ge",
          "label": "GE",
          "value": "ge",
          "count": 45,
          "filterUrl": "..."
        }
      ]
    },
    {
      "filterGroupId": "capacity",
      "filterGroupName": "Capacity",
      "filterType": "checkbox",
      "options": [...]
    }
  ],
  
  "products": [
    {
      "productId": "320243591",
      "modelNumber": "GNE27JYMFS",
      "brand": "GE",
      "title": "27 cu. ft. French Door Refrigerator...",
      "price": {
        "current": 1399.00,
        "original": 2599.00,
        "savings": 1200.00,
        "savingsPercent": 46
      },
      "rating": {
        "average": 4.4,
        "count": 13272
      },
      "images": {...},
      "badges": ["energyStar", "topSeller"],
      "availability": {...}
    }
  ]
}
```

## 🏷️ Product Detail Structure

Product detail files (`products/[productId]/details.json`) contain:

```json
{
  "productId": "320243591",
  
  "identifiers": {
    "internetNumber": "320243591",
    "modelNumber": "GNE27JYMFS",
    "storeSkuNumber": "1004567890",
    "upc": "084691838456"
  },
  
  "brand": {
    "name": "GE",
    "logoUrl": "https://.../ge-logo.svg",
    "series": "Standard"
  },
  
  "title": "27 cu. ft. French Door Refrigerator...",
  "shortDescription": "Internal water dispenser...",
  "longDescription": "This GE 27 cu. ft. French Door...",
  
  "breadcrumbs": [...],
  
  "pricing": {
    "currentPrice": 1399.00,
    "originalPrice": 2599.00,
    "savings": 1200.00,
    "savingsPercent": 46,
    "financing": {
      "monthlyPayment": 117.00,
      "term": 12,
      "apr": 0
    }
  },
  
  "rating": {
    "average": 4.4,
    "count": 13272,
    "recommendationPercent": 86,
    "distribution": {
      "5star": 8425,
      "4star": 2654,
      "3star": 1062,
      "2star": 530,
      "1star": 601
    }
  },
  
  "media": {
    "primaryImage": "...",
    "images": [
      {"url": "...", "altText": "...", "type": "primary"},
      {"url": "...", "altText": "...", "type": "detail"}
    ],
    "videos": [...],
    "has360View": true
  },
  
  "variants": [
    {
      "variantId": "320243614",
      "name": "Black Stainless",
      "color": "Black Stainless Steel",
      "swatchUrl": "...",
      "pricing": {...}
    }
  ],
  
  "keyFeatures": [
    "Internal Water Dispenser",
    "Ice Maker",
    "Fingerprint Resistant"
  ],
  
  "specifications": {
    "dimensions": {
      "width": "35.75 in.",
      "depth": "36.25 in.",
      "height": "69.88 in.",
      "capacity": "26.7 cu. ft."
    },
    "features": {...},
    "electrical": {...}
  },
  
  "badges": [
    {"type": "energyStar", "label": "ENERGY STAR"},
    {"type": "topSeller", "label": "Top Seller"}
  ],
  
  "availability": {
    "inStorePickup": true,
    "delivery": true,
    "shipToHome": false
  },
  
  "relatedProducts": {
    "accessories": [...],
    "similar": [...],
    "frequentlyBoughtTogether": [...]
  }
}
```

## 🔍 Filter Types

### 1. Checkbox Filters
Multi-select facets for brands, features, specifications.

```json
{
  "filterGroupId": "brand",
  "filterGroupName": "Brand",
  "filterType": "checkbox",
  "options": [
    {
      "optionId": "ge",
      "label": "GE",
      "value": "ge",
      "count": 45
    }
  ]
}
```

### 2. Range Filters
Price ranges and numeric values.

```json
{
  "filterGroupId": "price",
  "filterGroupName": "Price",
  "filterType": "range",
  "options": [
    {
      "optionId": "1000-2000",
      "label": "$1000 - $2000",
      "value": "1000-2000",
      "count": 85
    }
  ]
}
```

### 3. Color Filters
Color family selection.

```json
{
  "filterGroupId": "color",
  "filterGroupName": "Color Family",
  "filterType": "color",
  "options": [
    {
      "optionId": "stainless-steel",
      "label": "Stainless Steel",
      "value": "stainless-steel",
      "count": 156
    }
  ]
}
```

## 🎨 Image Organization

### Product Images
- **Location:** `images/products/`
- **Format:** AVIF, WebP, JPG
- **Size:** 600px width
- **Naming:** Numbered from scraped manifests

### Brand Logos
- **Location:** `images/brands/`
- **Format:** SVG (vector)
- **Usage:** Featured brands, product cards

### UI Elements
- **Location:** `images/ui/`
- **Format:** SVG
- **Examples:** Energy Star badge, Top Seller icon

### Hero Images
- **Location:** `images/heroes/`
- **Format:** AVIF, JPG, PNG
- **Size:** Various (typically 703px+)
- **Usage:** Category headers, promotional banners

## 🗺️ Navigation Taxonomy

The navigation follows a hierarchical structure:

```
Department (15)
└── Category Group
    └── Category
        └── Subcategory
```

**Example:**
```
Appliances
└── Refrigerators
    ├── French Door Refrigerators
    ├── Side by Side Refrigerators
    ├── Top Freezer Refrigerators
    ├── Bottom Freezer Refrigerators
    ├── Mini Fridges
    └── Freezerless Refrigerators
```

### Human-Readable IDs

All category IDs are lowercase, hyphenated, and hierarchical:

- `appliances` (department)
- `appliances/refrigerators` (category group)
- `appliances/refrigerators/french-door` (category)

## 📱 iOS App Integration

### Navigation Flow

1. **Load `categories/index.json`** for department tree
2. **Display department grid** (15 departments)
3. **User taps department** → Load subcategories
4. **User taps category** → Load category JSON with products & filters
5. **User applies filters** → Filter products locally or build filter URL
6. **User taps product** → Load product detail from `products/[id]/details.json`

### Filtering Implementation

**Client-Side Filtering (Recommended for POC):**
```swift
// Filter products by brand
let geProducts = category.products.filter { product in
    product.brand.lowercased() == "ge"
}

// Filter by multiple attributes
let filtered = category.products.filter { product in
    selectedBrands.contains(product.brand) &&
    product.price.current >= priceMin &&
    product.price.current <= priceMax &&
    product.badges.contains("energyStar")
}
```

**Server-Side Filtering (Future):**
Use `filterUrl` from filter options to construct API calls to live Home Depot data.

### Quick Filters

Display quick filters as visual tiles:
```swift
ForEach(category.quickFilters) { filter in
    QuickFilterTile(
        label: filter.label,
        imageURL: filter.imageUrl
    )
    .onTapGesture {
        // Apply filter or navigate to filterUrl
    }
}
```

### Product Cards

Display products in grid/list with:
- Primary image (600px)
- Brand logo (SVG)
- Title
- Current price + savings
- Star rating + count
- Badges (Top Seller, Energy Star, etc.)

### Product Detail View

Load full product data:
```swift
if let product = loadProduct(id: productId) {
    ProductDetailView(
        images: product.media.images,
        variants: product.variants,
        specs: product.specifications,
        features: product.keyFeatures,
        rating: product.rating,
        relatedProducts: product.relatedProducts
    )
}
```

## 🔧 Subcategory Attributes

Products are tagged with attributes for filtering:

**Example: French Door Refrigerator**
- **Category Path:** `["Appliances", "Refrigerators", "French Door"]`
- **Filter Tags:**
  - `brand: "ge"`
  - `capacity: "25-27"`
  - `doors: "3-door"`
  - `color: "stainless-steel"`
  - `features: ["counter-depth", "ice-maker", "smart", "energy-star"]`

**Filtering by Subcategory:**
```swift
// Show only Counter Depth models
let counterDepth = products.filter { product in
    product.filterTags.features.contains("counter-depth")
}

// Show only Energy Star certified
let energyEfficient = products.filter { product in
    product.badges.contains(where: { $0.type == "energyStar" })
}
```

## 🌐 GitHub Pages Deployment

### URL Structure
```
https://[username].github.io/orange-catalog/
├── categories/
│   ├── index.json
│   ├── appliances/
│   │   ├── dishwashers.json
│   │   └── refrigerators/
│   │       └── french-door.json
├── products/
│   └── 320243591/
│       └── details.json
└── images/
    ├── products/
    ├── brands/
    └── heroes/
```

### iOS API Calls
```swift
let baseURL = "https://[username].github.io/orange-catalog"

// Load navigation
let navURL = "\(baseURL)/categories/index.json"

// Load category
let categoryURL = "\(baseURL)/categories/appliances/refrigerators/french-door.json"

// Load product
let productURL = "\(baseURL)/products/320243591/details.json"

// Load image
let imageURL = "\(baseURL)/images/products/35.avif"
```

## 📝 Data Schemas

### Category Schema
See: `_source data/plp-schema.json`

### Product Schema  
See: `_source data/pip-schema.json`

All production JSON files follow these schemas.

## ⚠️ Important Notes

1. **Image URLs:** Currently reference local numbered files. Update paths to GitHub Pages URLs after deployment.

2. **Filter URLs:** Original Home Depot filter URLs are preserved but won't work without live API. Implement client-side filtering instead.

3. **Product Counts:** May not match live Home Depot due to static snapshot.

4. **Data Freshness:** Snapshot from Dec 31, 2025. No auto-updates.

5. **Missing Data:** Some categories may have limited products/filters based on what was scraped.

## 🚀 Quick Start for iOS

1. **Clone/Download** production data folder
2. **Upload to GitHub Pages** or CDN
3. **Update base URL** in app configuration
4. **Load** `categories/index.json` on app launch
5. **Build navigation** from category tree
6. **Display categories** with product counts
7. **Implement filtering** using filter definitions
8. **Load product details** on demand

## 📊 Statistics

- **Departments:** 15
- **Categories:** 88  
- **Products:** 30 (with full details)
- **Filter Groups:** Varies by category
- **Brands:** 185+ with logos
- **Images:** 539 optimized assets
- **Total Size:** 11 MB

---

**Generated by:** Orange Catalog Data Transformation Script  
**Contact:** For questions about data structure or iOS integration  
**Last Updated:** December 31, 2025
