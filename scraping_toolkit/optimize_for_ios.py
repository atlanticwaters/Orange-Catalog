#!/usr/bin/env python3
"""
Optimize production data for iOS consumption:
1. Update image URLs to use relative paths for local images
2. Add API manifest for version control and caching
3. Add checksums for data integrity
4. Create Swift-friendly structure documentation
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def update_image_urls():
    """Update product image URLs to use relative paths for local images"""
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    products_dir = base_path / 'production data' / 'products'
    
    print('🔄 Updating image URLs to relative paths...')
    updated_count = 0
    
    for product_folder in products_dir.iterdir():
        if not product_folder.is_dir():
            continue
            
        details_file = product_folder / 'details.json'
        if not details_file.exists():
            continue
        
        # Load product details
        with open(details_file, 'r') as f:
            product = json.load(f)
        
        # Check if product has image
        image_url = product.get('media', {}).get('primaryImage', '')
        if image_url and image_url.startswith('https://'):
            # Find local image file
            filename = image_url.split('/')[-1]
            local_image = product_folder / filename
            
            if local_image.exists():
                # Update to relative path
                relative_path = f"/products/{product_folder.name}/{filename}"
                product['media']['primaryImage'] = relative_path
                
                # Update images array too
                if 'images' in product['media'] and product['media']['images']:
                    product['media']['images'][0]['url'] = relative_path
                
                # Save updated product
                with open(details_file, 'w') as f:
                    json.dump(product, f, indent=2)
                
                updated_count += 1
    
    print(f'   ✅ Updated {updated_count:,} product image URLs')
    return updated_count

def create_api_manifest():
    """Create API manifest with version info and file checksums"""
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    production_dir = base_path / 'production data'
    
    print('📋 Creating API manifest...')
    
    manifest = {
        "version": "1.0.0",
        "generatedAt": datetime.now().isoformat(),
        "apiVersion": "v1",
        "endpoints": {
            "summary": "/SUMMARY.json",
            "categories": "/categories/index.json",
            "categoryDetails": "/categories/{department}/{category}.json",
            "productDetails": "/products/{productId}/details.json",
            "productImage": "/products/{productId}/{imageFileName}"
        },
        "dataIntegrity": {
            "summary": calculate_file_hash(production_dir / 'SUMMARY.json'),
            "categoriesIndex": calculate_file_hash(production_dir / 'categories' / 'index.json')
        },
        "caching": {
            "recommendedTTL": {
                "summary": 3600,
                "categories": 3600,
                "products": 86400,
                "images": 2592000
            }
        },
        "metadata": {
            "totalProducts": 0,
            "totalCategories": 0,
            "totalImages": 0,
            "dataSize": {
                "json": 0,
                "images": 0
            }
        }
    }
    
    # Calculate metadata
    summary_data = json.load(open(production_dir / 'SUMMARY.json'))
    manifest['metadata']['totalProducts'] = summary_data['dataStats']['totalProducts']
    manifest['metadata']['totalCategories'] = summary_data['dataStats']['totalCategories']
    
    # Count images and calculate sizes
    products_dir = production_dir / 'products'
    image_count = 0
    json_size = 0
    image_size = 0
    
    for product_folder in products_dir.iterdir():
        if product_folder.is_dir():
            for file in product_folder.iterdir():
                file_size = file.stat().st_size
                if file.suffix == '.json':
                    json_size += file_size
                elif file.suffix in ['.jpg', '.jpeg', '.png', '.webp', '.avif']:
                    image_size += file_size
                    image_count += 1
    
    manifest['metadata']['totalImages'] = image_count
    manifest['metadata']['dataSize']['json'] = f"{json_size / 1024 / 1024:.2f} MB"
    manifest['metadata']['dataSize']['images'] = f"{image_size / 1024 / 1024:.2f} MB"
    
    # Save manifest
    manifest_file = production_dir / 'api-manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f'   ✅ Created API manifest')
    print(f'      - {manifest["metadata"]["totalProducts"]:,} products')
    print(f'      - {manifest["metadata"]["totalCategories"]} categories')
    print(f'      - {manifest["metadata"]["totalImages"]:,} images')
    print(f'      - JSON: {manifest["metadata"]["dataSize"]["json"]}')
    print(f'      - Images: {manifest["metadata"]["dataSize"]["images"]}')
    
    return manifest

def create_swift_models_documentation():
    """Create documentation for Swift Codable models"""
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    
    swift_docs = """# Swift Models for Orange Catalog

## Data Structures

All JSON data is designed to work seamlessly with Swift's `Codable` protocol.

### Product Model

```swift
struct Product: Codable, Identifiable {
    let productId: String
    let identifiers: Identifiers
    let brand: Brand
    let title: String
    let shortDescription: String
    let longDescription: String
    let pricing: Pricing
    let rating: Rating
    let media: Media
    let availability: Availability
    let badges: [String]
    let specifications: [String: String]
    let shipping: Shipping
    let version: String
    let lastUpdated: String
    
    var id: String { productId }
    
    struct Identifiers: Codable {
        let internetNumber: String
        let modelNumber: String
        let storeSkuNumber: String
    }
    
    struct Brand: Codable {
        let name: String
        let logoUrl: String
    }
    
    struct Pricing: Codable {
        let currentPrice: Double
        let currency: String
    }
    
    struct Rating: Codable {
        let average: Double
        let count: Int
    }
    
    struct Media: Codable {
        let primaryImage: String
        let images: [ProductImage]
        
        struct ProductImage: Codable {
            let url: String
            let altText: String
            let type: String
        }
    }
    
    struct Availability: Codable {
        let inStock: Bool
        let availableForPickup: Bool
        let availableForDelivery: Bool
    }
    
    struct Shipping: Codable {
        let freeShipping: Bool
    }
}
```

### Category Model

```swift
struct Category: Codable, Identifiable {
    let categoryId: String
    let name: String
    let slug: String
    let path: String
    let version: String
    let lastUpdated: String
    let breadcrumbs: [Breadcrumb]
    let pageInfo: PageInfo
    let featuredBrands: [FeaturedBrand]
    let products: [ProductSummary]
    
    var id: String { categoryId }
    
    struct Breadcrumb: Codable {
        let label: String
        let url: String
    }
    
    struct PageInfo: Codable {
        let totalResults: Int
    }
    
    struct FeaturedBrand: Codable {
        let brandId: String
        let brandName: String
        let logoUrl: String
        let count: Int
    }
    
    struct ProductSummary: Codable, Identifiable {
        let productId: String
        let title: String
        let brand: String
        let price: Double
        let rating: Double
        let reviewCount: Int
        let imageUrl: String
        let inStock: Bool
        
        var id: String { productId }
    }
}
```

### Summary Model

```swift
struct CatalogSummary: Codable {
    let version: String
    let generatedAt: String
    let dataStats: DataStats
    let topBrands: [TopBrand]
    let topCategories: [TopCategory]
    
    struct DataStats: Codable {
        let totalCategories: Int
        let totalProducts: Int
        let totalBrands: Int
        let categoriesWithProducts: Int
    }
    
    struct TopBrand: Codable {
        let name: String
        let productCount: Int
    }
    
    struct TopCategory: Codable {
        let path: String
        let name: String
        let productCount: Int
    }
}
```

### API Manifest Model

```swift
struct APIManifest: Codable {
    let version: String
    let generatedAt: String
    let apiVersion: String
    let endpoints: Endpoints
    let dataIntegrity: DataIntegrity
    let caching: Caching
    let metadata: Metadata
    
    struct Endpoints: Codable {
        let summary: String
        let categories: String
        let categoryDetails: String
        let productDetails: String
        let productImage: String
    }
    
    struct DataIntegrity: Codable {
        let summary: String
        let categoriesIndex: String
    }
    
    struct Caching: Codable {
        let recommendedTTL: RecommendedTTL
        
        struct RecommendedTTL: Codable {
            let summary: Int
            let categories: Int
            let products: Int
            let images: Int
        }
    }
    
    struct Metadata: Codable {
        let totalProducts: Int
        let totalCategories: Int
        let totalImages: Int
        let dataSize: DataSize
        
        struct DataSize: Codable {
            let json: String
            let images: String
        }
    }
}
```

## Usage Examples

### Loading the API Manifest

```swift
func loadAPIManifest() async throws -> APIManifest {
    let url = URL(string: "https://yourusername.github.io/Orange-Catalog/api-manifest.json")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(APIManifest.self, from: data)
}
```

### Loading a Product

```swift
func loadProduct(id: String) async throws -> Product {
    let url = URL(string: "https://yourusername.github.io/Orange-Catalog/products/\\(id)/details.json")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(Product.self, from: data)
}
```

### Loading a Category

```swift
func loadCategory(department: String, category: String) async throws -> Category {
    let url = URL(string: "https://yourusername.github.io/Orange-Catalog/categories/\\(department)/\\(category).json")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(Category.self, from: data)
}
```

### Caching Strategy

Use the recommended TTL values from the API manifest for URLCache:

```swift
let cache = URLCache(
    memoryCapacity: 50 * 1024 * 1024,  // 50 MB
    diskCapacity: 100 * 1024 * 1024     // 100 MB
)

let config = URLSessionConfiguration.default
config.urlCache = cache
config.requestCachePolicy = .returnCacheDataElseLoad

let session = URLSession(configuration: config)
```

### Image Loading

Product images use relative paths. Construct full URLs like:

```swift
func imageURL(for product: Product, baseURL: String) -> URL? {
    guard let relativePath = product.media.primaryImage else { return nil }
    return URL(string: baseURL + relativePath)
}

// Usage:
let baseURL = "https://yourusername.github.io/Orange-Catalog"
if let imageURL = imageURL(for: product, baseURL: baseURL) {
    // Load image with AsyncImage or URLSession
}
```

## GitHub Pages Setup

1. Enable GitHub Pages in repository settings
2. Set source to main branch / root
3. Your data will be available at: `https://[username].github.io/[repo-name]/`

## Data Validation

All checksums in the API manifest use SHA256. Verify data integrity:

```swift
import CryptoKit

func verifySHA256(_ data: Data, expectedHash: String) -> Bool {
    let hash = SHA256.hash(data: data)
    let hashString = hash.compactMap { String(format: "%02x", $0) }.joined()
    return hashString == expectedHash
}
```
"""
    
    docs_file = base_path / 'production data' / 'SWIFT_MODELS.md'
    with open(docs_file, 'w') as f:
        f.write(swift_docs)
    
    print(f'   ✅ Created Swift models documentation')
    return docs_file

def create_github_pages_config():
    """Create _config.yml for GitHub Pages"""
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    
    config = """# GitHub Pages Configuration for Orange Catalog

# Serve JSON files with correct MIME type
include:
  - "_*"
  - "*.json"
  - "production data"

# No Jekyll processing - serve files as-is
markdown: false
highlighter: false

# MIME types
defaults:
  - scope:
      path: "**/*.json"
    values:
      layout: none

# Enable CORS for API access
plugins:
  - jekyll-cors
"""
    
    config_file = base_path / '_config.yml'
    with open(config_file, 'w') as f:
        f.write(config)
    
    print(f'   ✅ Created GitHub Pages config')
    return config_file

def create_nojekyll():
    """Create .nojekyll file to bypass Jekyll processing"""
    base_path = Path('/Users/awaters/Documents/GitHub/Orange Catalog')
    nojekyll_file = base_path / '.nojekyll'
    nojekyll_file.touch()
    print(f'   ✅ Created .nojekyll file')
    return nojekyll_file

def main():
    print('='*70)
    print('🚀 Optimizing Production Data for iOS')
    print('='*70)
    print()
    
    # Step 1: Update image URLs
    print('📱 Step 1: Update image URLs to relative paths')
    updated_count = update_image_urls()
    print()
    
    # Step 2: Create API manifest
    print('📋 Step 2: Create API manifest')
    manifest = create_api_manifest()
    print()
    
    # Step 3: Create Swift documentation
    print('📚 Step 3: Create Swift models documentation')
    docs_file = create_swift_models_documentation()
    print()
    
    # Step 4: GitHub Pages setup
    print('⚙️  Step 4: Configure GitHub Pages')
    create_github_pages_config()
    create_nojekyll()
    print()
    
    print('='*70)
    print('✨ iOS Optimization Complete!')
    print('='*70)
    print()
    print('📱 iOS-Ready Features:')
    print(f'   ✅ {updated_count:,} products with relative image paths')
    print(f'   ✅ API manifest with checksums and caching hints')
    print(f'   ✅ Swift Codable models documentation')
    print(f'   ✅ GitHub Pages configuration')
    print()
    print('📋 Next Steps:')
    print('   1. Review production data/SWIFT_MODELS.md')
    print('   2. Commit and push to GitHub')
    print('   3. Enable GitHub Pages in repository settings')
    print('   4. Access your API at: https://[username].github.io/Orange-Catalog/')
    print()

if __name__ == '__main__':
    main()
