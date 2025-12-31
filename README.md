# 🍊 Orange Catalog

A comprehensive, production-ready dataset of Home Depot product catalog data, optimized for mobile app development and web applications.

[![Data Version](https://img.shields.io/badge/version-1.0-orange.svg)](https://github.com/atlanticwaters/Orange-Catalog)
[![Total Products](https://img.shields.io/badge/products-2,607-blue.svg)](#)
[![Categories](https://img.shields.io/badge/categories-88-green.svg)](#)
[![Images](https://img.shields.io/badge/images-539-purple.svg)](#)

---

## 📋 Overview

Orange Catalog provides structured JSON data for building product catalog applications, with a focus on:

- **Clean, hierarchical taxonomy** - Human-readable category IDs
- **Comprehensive filtering** - Multi-faceted search with counts
- **Optimized images** - 600px product images + SVG logos
- **Mobile-first design** - Perfect for iOS/Android apps
- **GitHub Pages ready** - Static hosting, no backend required

**Snapshot Date:** December 31, 2025  
**Total Size:** 11 MB

---

## 🚀 Quick Start

### For iOS/Swift Developers

```swift
// 1. Set your base URL
let baseURL = "https://atlanticwaters.github.io/Orange-Catalog/production%20data"

// 2. Load the navigation tree
let navURL = URL(string: "\(baseURL)/categories/index.json")!
let navigation = try await URLSession.shared.decode(Navigation.self, from: navURL)

// 3. Load a category with products
let categoryURL = URL(string: "\(baseURL)/categories/appliances/refrigerators/french-door.json")!
let category = try await URLSession.shared.decode(Category.self, from: categoryURL)

// 4. Display products with filtering
let filteredProducts = category.products.filter { product in
    selectedBrands.contains(product.brand)
}
```

### For Web Developers

```javascript
// Fetch navigation
const navigation = await fetch('https://atlanticwaters.github.io/Orange-Catalog/production%20data/categories/index.json')
  .then(res => res.json());

// Fetch category data
const category = await fetch('https://atlanticwaters.github.io/Orange-Catalog/production%20data/categories/appliances/dishwashers.json')
  .then(res => res.json());

// Display products
category.products.forEach(product => {
  console.log(`${product.brand} ${product.title} - $${product.price.current}`);
});
```

---

## 📊 What's Inside

### Data Summary

| Resource | Count | Description |
|----------|-------|-------------|
| **Categories** | 88 | Complete product categories across 15 departments |
| **Products** | 2,607 | Product IDs with basic information |
| **Full Details** | 30 | Complete product specifications (PIP data) |
| **Images** | 539 | Optimized product images, brand logos, and assets |
| **Departments** | 15 | Top-level navigation categories |

### Departments

- 🏠 **Appliances** - Refrigerators, Dishwashers, Ranges, Microwaves, etc.
- 🛠️ **Tools** - Drills, Saws, Impact Drivers, Power Tools, etc.
- 🌳 **Outdoors** - Lawn Mowers, Power Equipment, etc.
- 🛁 **Bath** - Fixtures, Vanities, etc.
- 🍳 **Kitchen** - Cabinets, Countertops, etc.
- 💡 **Lighting** - Indoor, Outdoor, Smart Lighting, etc.
- 🚿 **Plumbing** - Pipes, Fixtures, Faucets, etc.
- ⚡ **Electrical** - Wiring, Outlets, Switches, etc.
- 🪟 **Flooring** - Hardwood, Tile, Carpet, etc.
- 🏗️ **Building Materials** - Lumber, Concrete, etc.
- 🧹 **Cleaning** - Vacuums, Supplies, etc.
- 🚗 **Garage** - Storage, Organization, etc.
- 🌺 **Garden Center** - Plants, Soil, Planters, etc.
- 🖼️ **Home Decor** - Furniture, Art, etc.
- 🪟 **Window Treatments** - Blinds, Curtains, etc.

---

## 🗂️ Directory Structure

```
production data/
├── categories/                  # Category JSON files
│   ├── index.json              # Master navigation tree
│   ├── appliances/
│   │   ├── dishwashers.json
│   │   ├── refrigerators/
│   │   │   ├── french-door.json
│   │   │   ├── side-by-side.json
│   │   │   └── ...
│   │   └── ...
│   ├── tools/
│   │   ├── drills.json
│   │   ├── impact-drivers.json
│   │   └── ...
│   └── ...
├── products/                    # Individual product details
│   ├── 320243591/
│   │   └── details.json
│   └── ...
├── images/                      # Optimized images
│   ├── products/               # 600px product images (175)
│   ├── brands/                 # SVG brand logos (185)
│   ├── ui/                     # Badges & icons (11)
│   └── heroes/                 # Category banners (168)
└── README.md                    # Detailed documentation
```

---

## 🔍 Category JSON Structure

Each category file provides everything needed for a product listing page:

```json
{
  "categoryId": "appliances/refrigerators/french-door",
  "name": "French Door Refrigerators",
  "breadcrumbs": [...],
  
  "featuredBrands": [
    {
      "brandName": "GE",
      "logoUrl": "https://images.thdstatic.com/catalog/brandLogos/ge-logo.svg"
    }
  ],
  
  "filters": [
    {
      "filterGroupId": "brand",
      "filterGroupName": "Brand",
      "filterType": "checkbox",
      "options": [
        {
          "label": "GE",
          "value": "ge",
          "count": 45
        }
      ]
    }
  ],
  
  "products": [
    {
      "productId": "320243591",
      "brand": "GE",
      "title": "27 cu. ft. French Door Refrigerator...",
      "price": {
        "current": 1399.00,
        "savings": 1200.00
      },
      "rating": {
        "average": 4.4,
        "count": 13272
      }
    }
  ]
}
```

---

## 🎨 Product Detail Structure

Full product specifications for detailed views:

```json
{
  "productId": "320243591",
  "brand": {
    "name": "GE",
    "logoUrl": "https://images.thdstatic.com/catalog/brandLogos/ge-logo.svg"
  },
  "title": "27 cu. ft. French Door Refrigerator...",
  "pricing": {
    "currentPrice": 1399.00,
    "originalPrice": 2599.00,
    "savings": 1200.00,
    "savingsPercent": 46
  },
  "rating": {
    "average": 4.4,
    "count": 13272,
    "distribution": {
      "5star": 8425,
      "4star": 2654
    }
  },
  "specifications": {
    "dimensions": {
      "width": "35.75 in.",
      "capacity": "26.7 cu. ft."
    }
  },
  "keyFeatures": [
    "Internal Water Dispenser",
    "ENERGY STAR Certified"
  ]
}
```

---

## 🔧 Filtering & Search

### Filter Types

The dataset supports three filter types:

#### 1. **Checkbox Filters** (Multi-select)
```json
{
  "filterGroupId": "brand",
  "filterType": "checkbox",
  "options": [
    {"label": "GE", "count": 45},
    {"label": "Samsung", "count": 38}
  ]
}
```

#### 2. **Range Filters** (Numeric)
```json
{
  "filterGroupId": "price",
  "filterType": "range",
  "options": [
    {"label": "$1000 - $2000", "count": 85}
  ]
}
```

#### 3. **Color Filters** (Swatches)
```json
{
  "filterGroupId": "color",
  "filterType": "color",
  "options": [
    {"label": "Stainless Steel", "count": 156}
  ]
}
```

### Quick Filters

Visual shortcuts for common filter combinations:

```json
{
  "quickFilters": [
    {
      "filterId": "counter-depth",
      "label": "Counter Depth",
      "imageUrl": "..."
    }
  ]
}
```

---

## 🌐 API Endpoints

When deployed to GitHub Pages, access data via clean URLs:

### Navigation
```
GET /production data/categories/index.json
```

### Categories
```
GET /production data/categories/appliances/dishwashers.json
GET /production data/categories/tools/drills.json
GET /production data/categories/outdoors/outdoor-power-equipment/lawn-mowers.json
```

### Products
```
GET /production data/products/320243591/details.json
```

### Images
```
GET /production data/images/products/35.avif
GET /production data/images/brands/ge.svg
GET /production data/images/heroes/appliances-hero.jpg
```

---

## 💡 Use Cases

### iOS/Android Apps
- Product catalog browsing
- Multi-faceted filtering
- Product detail views
- Shopping cart prototypes

### Web Applications
- E-commerce UI testing
- Search & filter demos
- Product comparison tools
- Design system showcases

### Learning & Education
- API integration practice
- Mobile app development
- React/Vue.js tutorials
- SwiftUI examples

---

## 🎯 Top Categories

| Category | Products | Path |
|----------|----------|------|
| Ice Makers | 75 | `categories/appliances/ice-makers.json` |
| Mini Fridges | 69 | `categories/appliances/mini-fridges.json` |
| Drill Bits | 62 | `categories/tools/drill-bits.json` |
| Lawn Mowers | 567 | `categories/outdoors/.../lawn-mowers.json` |
| Impact Wrenches | 51 | `categories/tools/impact-wrenches.json` |

---

## 📱 Example: iOS App Integration

### 1. Create Models

```swift
struct Navigation: Codable {
    let departments: [Department]
}

struct Department: Codable {
    let id: String
    let name: String
    let slug: String
    let subcategories: [Subcategory]
}

struct Category: Codable {
    let categoryId: String
    let name: String
    let breadcrumbs: [Breadcrumb]
    let filters: [FilterGroup]
    let products: [Product]
}

struct Product: Codable {
    let productId: String
    let brand: String
    let title: String
    let price: Price
    let rating: Rating
}
```

### 2. Build Navigation

```swift
class CatalogService {
    let baseURL = "https://atlanticwaters.github.io/Orange-Catalog/production%20data"
    
    func loadNavigation() async throws -> Navigation {
        let url = URL(string: "\(baseURL)/categories/index.json")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(Navigation.self, from: data)
    }
    
    func loadCategory(path: String) async throws -> Category {
        let url = URL(string: "\(baseURL)/categories/\(path).json")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(Category.self, from: data)
    }
}
```

### 3. Display Products

```swift
struct ProductGridView: View {
    let category: Category
    @State private var selectedBrands: Set<String> = []
    
    var filteredProducts: [Product] {
        category.products.filter { product in
            selectedBrands.isEmpty || selectedBrands.contains(product.brand)
        }
    }
    
    var body: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 160))]) {
                ForEach(filteredProducts, id: \.productId) { product in
                    ProductCard(product: product)
                }
            }
        }
    }
}
```

---

## 🛠️ Development

### Clone Repository

```bash
git clone https://github.com/atlanticwaters/Orange-Catalog.git
cd Orange-Catalog
```

### Validate Data

```bash
python3 validate_data.py
```

### Local Testing

Serve locally with Python:

```bash
cd "production data"
python3 -m http.server 8000
```

Access at: `http://localhost:8000/categories/index.json`

---

## 📊 Data Statistics

- **Total Size:** 11 MB (GitHub Pages friendly)
- **JSON Files:** 119 (88 categories + 30 products + 1 index)
- **Image Formats:** AVIF, WebP, JPG, PNG, SVG
- **Image Optimization:** 600px width for product images
- **Valid JSON:** 97.7% (only index files lack categoryId)

---

## ⚠️ Important Notes

### Data Freshness
- Static snapshot from **December 31, 2025**
- No automatic updates
- Perfect for prototyping and UI development

### Image URLs
- Images are organized and optimized
- Brand logos are SVG for perfect scaling
- All images referenced in JSON

### Filter Implementation
- Filter URLs reference original Home Depot structure
- Implement client-side filtering for best results
- Use filter counts to show available options

### Product Coverage
- **2,607 product IDs** for UI mockups
- **30 products** with full specifications
- Great for testing, expand as needed

---

## 📄 License

This dataset is provided for educational and development purposes. Product data is sourced from publicly available information. Please respect Home Depot's terms of service and trademarks.

---

## 🤝 Contributing

Found an issue or want to improve the dataset?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

- **Documentation:** See `production data/README.md` for detailed API reference
- **Issues:** [GitHub Issues](https://github.com/atlanticwaters/Orange-Catalog/issues)
- **Discussions:** [GitHub Discussions](https://github.com/atlanticwaters/Orange-Catalog/discussions)

---

## 🎉 Acknowledgments

Created with:
- Python data transformation scripts
- BeautifulSoup for HTML parsing
- JSON validation and optimization
- Love for clean, usable data ❤️

---

**Made with 🍊 by [atlanticwaters](https://github.com/atlanticwaters)**

*Perfect for iOS apps, web applications, and learning projects.*
