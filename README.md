# 🍊 Orange Catalog

A comprehensive, production-ready product catalog dataset optimized for iOS apps, web applications, and API consumption. Contains 3,000+ home improvement products from The Home Depot with complete metadata, images, and search capabilities.

[![Data Version](https://img.shields.io/badge/version-1.0-orange.svg)](https://github.com/atlanticwaters/Orange-Catalog)
[![Total Products](https://img.shields.io/badge/products-3,001-blue.svg)](#)
[![Categories](https://img.shields.io/badge/categories-76-green.svg)](#)
[![Brands](https://img.shields.io/badge/brands-372-purple.svg)](#)
[![Live Demo](https://img.shields.io/badge/demo-live-success.svg)](https://atlanticwaters.github.io/Orange-Catalog/)

---

## 🎯 Purpose

This repository serves as a **backend-free product catalog system** that provides:

1. **Static JSON API** - All data accessible via GitHub Pages (no server required)
2. **iOS App Integration** - Complete Swift models, caching strategy, and offline support
3. **Web Storefront** - Live browseable catalog with search and categories
4. **Search Infrastructure** - Pre-built search indexes for instant results
5. **Image Assets** - Optimized 100x100px product images (additional sizes can be generated)
6. **Update Management** - Version tracking and delta update support

Perfect for building product catalog apps without maintaining backend infrastructure.

---

## 📊 What's Inside

### Data Files
- **3,001 products** across 76 categories (tools, appliances, plumbing, etc.)
- **372 brands** including Milwaukee, DEWALT, RIDGID, Husky, LG, GE, etc.
- **Complete product details** - titles, descriptions, pricing, ratings, specs
- **Optimized images** - 100x100px JPEGs (~30MB total)
- **Category hierarchy** - Organized by department and subcategory

### API Files
- **app-config.json** - App configuration, endpoints, caching rules, features
- **search-index.json** - Full product search index with keywords (~3MB)
- **search-index-compact.json** - Mobile-optimized search (~2MB)
- **offline-catalog.json** - Lightweight offline mode data (~14KB)
- **featured-content.json** - Curated home screen content
- **update-manifest.json** - Version tracking and change management
- **deeplink-map.json** - URL scheme mapping for deep linking

### Tools & Scripts
- **Scraping toolkit** - Python scripts for data collection from The Home Depot
- **Data generators** - Create search indexes, offline catalogs, image variants
- **Automation scripts** - One-click data generation and updates

---

## 🚀 Quick Start

### Live Demo
**Browse the catalog:** https://atlanticwaters.github.io/Orange-Catalog/

### Base API URL
```
https://atlanticwaters.github.io/Orange-Catalog/production data/
```

### For iOS/Swift Developers

See **[iOS-INTEGRATION.md](iOS-INTEGRATION.md)** for complete integration guide with Swift code examples.

```swift
// 1. Load app configuration
let baseURL = "https://atlanticwaters.github.io/Orange-Catalog/production%20data"
let config = try await loadJSON(AppConfig.self, from: "\(baseURL)/app-config.json")

// 2. Fetch categories
let categories = try await loadJSON(CategoryIndex.self, from: "\(baseURL)/categories/index.json")

// 3. Get products by category
let products = try await loadJSON(CategoryData.self, from: "\(baseURL)/categories/tools.json")

// 4. Search products
let searchIndex = try await loadJSON(SearchIndex.self, from: "\(baseURL)/search-index-compact.json")
```

### For Web Developers

```javascript
// Fetch categories
const response = await fetch('https://atlanticwaters.github.io/Orange-Catalog/production data/categories/index.json');
const { categories } = await response.json();

// Get products in a category
const toolsResponse = await fetch('https://atlanticwaters.github.io/Orange-Catalog/production data/categories/tools.json');
const { products } = await toolsResponse.json();

// Display product
products.forEach(product => {
  const img = `production data/products/${product.product_id}/${product.image_url}`;
  console.log(`${product.name} - $${product.price}`);
});
```

---

## 📁 Repository Structure

```
Orange-Catalog/
├── production data/               # All catalog data (ready to serve)
│   ├── categories/               # Category data files
│   │   ├── index.json           # Category listing
│   │   ├── tools.json           # Products in tools category
│   │   ├── appliances.json      # Products in appliances
│   │   └── ...                  # 76 category files
│   │
│   ├── products/                # Individual product data
│   │   ├── 336149463/           # Product ID folder
│   │   │   ├── details.json     # Full product details
│   │   │   └── *.jpg            # Product image (100x100)
│   │   └── ...                  # 3,001 product folders
│   │
│   ├── brands/                  # Brand data (future use)
│   ├── images/                  # Shared images
│   │
│   ├── SUMMARY.json             # Catalog statistics
│   ├── app-config.json          # iOS app configuration
│   ├── search-index.json        # Full search index
│   ├── search-index-compact.json # Mobile search index
│   ├── offline-catalog.json     # Offline mode data
│   ├── featured-content.json    # Home screen content
│   ├── update-manifest.json     # Version tracking
│   ├── deeplink-map.json        # URL schemes
│   └── api-manifest.json        # API documentation
│
├── scraping_toolkit/            # Data collection scripts
│   ├── scrape_plp.py           # Product list scraper
│   ├── scrape_pip.py           # Product detail scraper
│   ├── process_images.py       # Image optimization
│   └── ...                     # More utilities
│
├── index.html                   # GitHub Pages home
├── category.html                # Category browser page
├── iOS-INTEGRATION.md           # Complete iOS guide
├── IOS_SETUP_COMPLETE.md        # iOS setup summary
└── README.md                    # This file
```

---

## 📊 Data Statistics

| Metric | Count | Details |
|--------|-------|---------|
| **Products** | 3,001 | Complete product entries with details |
| **Categories** | 76 | Organized by department |
| **Brands** | 372 | Milwaukee, DEWALT, RIDGID, Husky, LG, etc. |
| **Images** | 3,001 | Optimized 100x100px JPEGs |
| **JSON Size** | 3.69 MB | All product and category data |
| **Image Size** | 30.40 MB | All product images |
| **Total Size** | ~34 MB | Complete catalog |

### Top Brands
- **Milwaukee**: 271 products (power tools)
- **Husky**: 228 products (storage, tools)
- **DEWALT**: 183 products (power tools)
- **RIDGID**: 127 products (power tools)
- **RYOBI**: 106 products (power tools)
- **Nearly Natural**: 111 products (artificial plants)
- **GE**: 92 products (appliances)
- **LG**: 86 products (appliances)
- **Whirlpool**: 64 products (appliances)
- **Samsung**: 58 products (appliances)

### Categories Include
🛠️ **Tools** • 🏠 **Appliances** • 🚿 **Plumbing** • ⚡ **Electrical**  
💡 **Lighting** • 🪵 **Flooring** • 🏗️ **Building Materials** • 🛁 **Bath**  
🍳 **Kitchen** • 🌺 **Garden Center** • 🚗 **Garage** • 📦 **Storage**  
🎨 **Home Decor** • 🪟 **Window Treatments** • 🧹 **Cleaning** • 🪑 **Furniture**

---

## 🔧 API Endpoints

All endpoints are relative to: `https://atlanticwaters.github.io/Orange-Catalog/production data/`

### Configuration
- `GET /app-config.json` - App configuration and feature flags
- `GET /SUMMARY.json` - Catalog statistics and top brands

### Categories
- `GET /categories/index.json` - List all categories
- `GET /categories/{categoryName}.json` - Products in category (e.g., `/categories/tools.json`)

### Products
- `GET /products/{productId}/details.json` - Full product details
- `GET /products/{productId}/{imageName}.jpg` - Product image

### Search & Discovery
- `GET /search-index.json` - Full search index (3 MB)
- `GET /search-index-compact.json` - Mobile-optimized (2 MB)
- `GET /offline-catalog.json` - Offline mode data (14 KB)
- `GET /featured-content.json` - Curated home screen content

### Metadata
- `GET /update-manifest.json` - Version and update info
- `GET /deeplink-map.json` - Deep link URL schemes
- `GET /api-manifest.json` - API documentation

---

## 📖 Example: Product Data Structure

```json
{
  "product_id": "336149463",
  "name": "Garvee 34 in. H Artificial Fiddle Leaf Fig Tree in Basket",
  "brand": "Garvee",
  "price": 96.99,
  "rating": 4.5,
  "review_count": 12,
  "category": "garden-center",
  "subcategory": "artificial-plants",
  "image_url": "garvee-artificial-trees-xd-zsn-pho-34hyfkcr-64_100.jpg",
  "in_stock": true,
  "specifications": {
    "Height": "34 in",
    "Width": "15 in",
    "Material": "Plastic",
    "Indoor/Outdoor": "Indoor"
  }
}
```

---

## 🛠️ Development Tools

### Scraping Toolkit
Located in `/scraping_toolkit/` - Python scripts for data collection:

- **scrape_plp.py** - Scrapes product listing pages (categories)
- **scrape_pip.py** - Scrapes individual product detail pages
- **batch_scraper.py** - Automated batch scraping
- **process_images.py** - Downloads and optimizes product images
- **transform_to_production.py** - Converts raw data to production format

### Data Generators
Scripts to create iOS app integration files:

- **generate_search_index.py** - Creates searchable product indexes
- **generate_offline_catalog.py** - Creates lightweight offline data
- **generate_image_variants.py** - Generates additional image sizes (50px, 200px, 400px)
- **generate_all_app_data.sh** - One-click automation for all generators

### Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Generate all iOS app data
./generate_all_app_data.sh

# With additional image sizes
./generate_all_app_data.sh --with-images

# Individual generators
python3 generate_search_index.py
python3 generate_offline_catalog.py
```

---

## 📱 iOS Integration

Complete iOS integration is ready out of the box. See **[iOS-INTEGRATION.md](iOS-INTEGRATION.md)** for:

- Swift model definitions (Codable structs)
- Network service implementation
- SwiftUI view examples
- Caching strategy with recommended TTLs
- Search implementation
- Offline mode setup
- Deep linking handlers
- Performance optimization tips

### Quick Integration

1. Copy Swift models from iOS-INTEGRATION.md
2. Configure URLSession with caching
3. Load app-config.json on app launch
4. Fetch categories and products
5. Implement search using pre-built index
6. Enable offline mode with offline-catalog.json

### Features Ready
✅ Search (pre-built indexes)  
✅ Favorites (client-side)  
✅ Offline mode (14KB catalog)  
✅ Categories (76 organized categories)  
✅ Product details (3,001 products)  
✅ Images (optimized 100x100)  
✅ Deep linking (URL schemes configured)  
✅ Caching (TTL strategy included)  

---

## 🌐 GitHub Pages Website

Live demo: **https://atlanticwaters.github.io/Orange-Catalog/**

Features:
- Browse all 76 categories
- Search products within categories
- View product details, images, and pricing
- Responsive mobile-friendly design
- Direct JSON API access

Files:
- `index.html` - Category browser
- `category.html` - Product listing page

---

## 🔄 Update Workflow

When adding or updating products:

```bash
# 1. Scrape new data (optional)
cd scraping_toolkit
python3 scrape_plp.py --category tools

# 2. Generate app integration files
cd ..
./generate_all_app_data.sh

# 3. Commit and push
git add -A
git commit -m "Update catalog data"
git push origin main

# Data goes live automatically via GitHub Pages!
```

---

## 📋 Use Cases

### Mobile Apps
- **iOS/Android catalog apps** - Complete backend via static JSON
- **Shopping apps** - Product browsing without server costs
- **Price comparison apps** - Structured pricing data
- **Inventory apps** - Track home improvement products

### Web Applications
- **E-commerce storefronts** - No backend required
- **Product comparison sites** - Rich product data
- **Deal trackers** - Price and availability monitoring
- **Educational projects** - Learn web/mobile development

### Data Science
- **Price analysis** - 3,000+ products with pricing
- **Brand analysis** - 372 brands across categories
- **Category analysis** - Product distribution
- **ML training data** - Product categorization, search

---

## 💾 Caching Recommendations

Optimize performance with proper caching:

| Resource Type | TTL | Rationale |
|--------------|-----|-----------|
| App Config | 5 min | Check for updates frequently |
| Categories | 1 hour | Structure rarely changes |
| Products | 24 hours | Prices/inventory updated daily |
| Images | 30 days | Static assets, rarely change |
| Search Index | 1 hour | Rebuild when catalog updates |
| Featured Content | 30 min | Dynamic promotional content |

### URLCache Configuration (iOS)

```swift
let cacheConfig = URLSessionConfiguration.default
cacheConfig.urlCache = URLCache(
    memoryCapacity: 50_000_000,   // 50 MB
    diskCapacity: 200_000_000,    // 200 MB
    diskPath: "catalog_cache"
)
```

---

## 🔎 Search Implementation

Two search index options:

1. **Full Index** (`search-index.json` - 3 MB)
   - Complete keyword mapping
   - All 3,001 products
   - Best for web applications

2. **Compact Index** (`search-index-compact.json` - 2 MB)
   - Mobile-optimized
   - Frequently-used keywords only
   - 35% smaller
   - Recommended for iOS/Android

### Search Features
- Keyword-based search
- Brand filtering
- Category filtering
- Fuzzy matching support
- Real-time results

---

## 📦 Offline Mode

Enable offline browsing with minimal data:

**offline-catalog.json** (14 KB)
- Top 10 products per category
- Popular brands list
- Category structure
- Essential metadata

Perfect for:
- First-launch experience
- Low connectivity scenarios
- Reduced data usage
- App store previews

---

## 🔗 Deep Linking

URL Scheme: `orangecatalog://`

### Supported Patterns
```
orangecatalog://product/{productId}
orangecatalog://category/{categoryId}
orangecatalog://search?q={query}
orangecatalog://brand/{brandName}
orangecatalog://featured/{sectionId}
```

### Universal Links
Domain: `atlanticwaters.github.io`

Automatically maps web URLs to app screens.

---

## 📄 License & Attribution

### Data Source
Product data sourced from **The Home Depot** (HomeDepot.com).  
Images and product information are property of their respective owners.

### Usage
This dataset is provided for:
- Educational purposes
- Personal projects
- App development learning
- Portfolio demonstrations

### Disclaimer
This is an independent project and is not affiliated with, endorsed by, or sponsored by The Home Depot, Inc. Product images, brand names, and trademarks are property of their respective owners.

For commercial use, please ensure compliance with The Home Depot's terms of service and obtain necessary permissions.

---

## 🤝 Contributing

Contributions welcome! Ways to help:

- **Add more products** - Expand the catalog
- **Improve data quality** - Fix inconsistencies
- **Add features** - New search capabilities
- **Optimize images** - Better compression
- **Documentation** - Improve guides and examples
- **Bug fixes** - Report issues

### Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run data generators if needed
5. Submit a pull request

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/atlanticwaters/Orange-Catalog/issues)
- **Documentation**: This README and iOS-INTEGRATION.md
- **Live Demo**: https://atlanticwaters.github.io/Orange-Catalog/
- **Updates**: Automatically via GitHub Pages

---

## 🗓️ Version History

### Version 1.0.0 (December 31, 2025)
- Initial release
- 3,001 products across 76 categories
- 372 brands
- Complete iOS app integration
- GitHub Pages website
- Search infrastructure
- Offline mode support
- Deep linking configuration

---

## 🎯 Roadmap

Future enhancements:
- [ ] Additional image sizes (200x200, 400x400)
- [ ] Product reviews and Q&A data
- [ ] Related products/recommendations
- [ ] Price history tracking
- [ ] Inventory status updates
- [ ] More product categories
- [ ] Enhanced search with filters
- [ ] GraphQL API layer
- [ ] Real-time price updates
- [ ] Product comparison tools

---

**Made with ❤️ for the developer community**

*Last Updated: December 31, 2025*
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
