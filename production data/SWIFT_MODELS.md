# Swift Models for Orange Catalog

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
    let url = URL(string: "https://yourusername.github.io/Orange-Catalog/products/\(id)/details.json")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(Product.self, from: data)
}
```

### Loading a Category

```swift
func loadCategory(department: String, category: String) async throws -> Category {
    let url = URL(string: "https://yourusername.github.io/Orange-Catalog/categories/\(department)/\(category).json")!
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
