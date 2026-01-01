# iOS App Integration Guide

Complete guide for integrating the Orange Catalog data into your iOS application.

## Quick Start

1. **Base URL**: `https://atlanticwaters.github.io/Orange-Catalog/production data/`
2. **App Config**: Load `app-config.json` first to get all endpoint configurations
3. **Authentication**: None required - all data is publicly accessible

## Key Files

### Configuration Files
- **app-config.json** - Main app configuration, endpoints, caching strategy
- **update-manifest.json** - Version tracking and delta updates
- **deeplink-map.json** - Deep link URL schemes and patterns
- **featured-content.json** - Curated content for home screen

### Data Files
- **SUMMARY.json** - Catalog statistics and top brands
- **categories/index.json** - All category listings
- **categories/{name}.json** - Products by category
- **products/{id}/details.json** - Full product details
- **search-index.json** - Pre-built search index (3MB)
- **search-index-compact.json** - Lightweight search (1.9MB)
- **offline-catalog.json** - Minimal data for offline mode (14KB)

### Image Assets
- **Thumbnail**: 50x50px - For lists and thumbnails
- **Small**: 100x100px - Default product images
- **Medium**: 200x200px - Product detail views
- **Large**: 400x400px - Full-screen gallery

## Swift Integration

### 1. Create Models

```swift
import Foundation

// MARK: - App Configuration
struct AppConfig: Codable {
    let appVersion: String
    let minimumAppVersion: String
    let dataVersion: String
    let lastUpdated: String
    let baseURL: String
    let endpoints: Endpoints
    let features: Features
    let caching: CachingConfig
    let images: ImageConfig
    
    struct Endpoints: Codable {
        let appConfig: String
        let summary: String
        let searchIndex: String
        let categories: String
        let categoryDetails: String
        let productDetails: String
        let productImage: String
        let featuredContent: String
    }
    
    struct Features: Codable {
        let search: Bool
        let favorites: Bool
        let offlineMode: Bool
        let categories: Bool
        let productDetails: Bool
    }
    
    struct CachingConfig: Codable {
        let strategy: String
        let ttl: TTL
        
        struct TTL: Codable {
            let appConfig: Int
            let summary: Int
            let searchIndex: Int
            let categories: Int
            let products: Int
            let images: Int
        }
    }
    
    struct ImageConfig: Codable {
        let sizes: ImageSizes
        let defaultSize: String
        
        struct ImageSizes: Codable {
            let thumbnail: String
            let small: String
            let medium: String
            let large: String
        }
    }
}

// MARK: - Product
struct Product: Codable, Identifiable {
    let productId: String
    let name: String
    let brand: String?
    let price: Double?
    let rating: Double?
    let reviewCount: Int?
    let category: String
    let imageUrl: String?
    
    var id: String { productId }
    
    enum CodingKeys: String, CodingKey {
        case productId = "product_id"
        case name, brand, price, rating
        case reviewCount = "review_count"
        case category
        case imageUrl = "image_url"
    }
}

// MARK: - Category
struct Category: Codable, Identifiable {
    let id: String
    let name: String
    let productCount: Int
    
    enum CodingKeys: String, CodingKey {
        case id, name
        case productCount = "product_count"
    }
}

// MARK: - Search Index
struct SearchIndex: Codable {
    let version: String
    let generatedAt: String
    let totalProducts: Int
    let products: [SearchProduct]
    let keywords: [String: [String]]
    let categories: [String: [String]]
    let brands: [String: [String]]
    
    struct SearchProduct: Codable, Identifiable {
        let id: String
        let name: String
        let brand: String
        let category: String
        let price: Double?
        let rating: Double?
        let keywords: [String]
        let imageUrl: String
    }
}
```

### 2. Create Network Service

```swift
import Foundation

class CatalogService {
    static let shared = CatalogService()
    
    private let baseURL = "https://atlanticwaters.github.io/Orange-Catalog/production%20data"
    private let session = URLSession.shared
    private var config: AppConfig?
    
    // MARK: - Initialization
    func loadConfiguration() async throws {
        let url = URL(string: "\(baseURL)/app-config.json")!
        let (data, _) = try await session.data(from: url)
        config = try JSONDecoder().decode(AppConfig.self, from: data)
    }
    
    // MARK: - Categories
    func fetchCategories() async throws -> [Category] {
        let url = URL(string: "\(baseURL)/categories/index.json")!
        let (data, _) = try await session.data(from: url)
        let response = try JSONDecoder().decode(CategoryIndex.self, from: data)
        return response.categories
    }
    
    struct CategoryIndex: Codable {
        let categories: [Category]
    }
    
    // MARK: - Products by Category
    func fetchProducts(for categoryId: String) async throws -> [Product] {
        let url = URL(string: "\(baseURL)/categories/\(categoryId).json")!
        let (data, _) = try await session.data(from: url)
        let response = try JSONDecoder().decode(CategoryResponse.self, from: data)
        return response.products
    }
    
    struct CategoryResponse: Codable {
        let categoryName: String
        let totalProducts: Int
        let products: [Product]
        
        enum CodingKeys: String, CodingKey {
            case categoryName = "category_name"
            case totalProducts = "total_products"
            case products
        }
    }
    
    // MARK: - Product Details
    func fetchProductDetails(productId: String) async throws -> ProductDetail {
        let url = URL(string: "\(baseURL)/products/\(productId)/details.json")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(ProductDetail.self, from: data)
    }
    
    // MARK: - Image URL
    func imageURL(for productId: String, size: String = "small") -> URL? {
        // Construct image URL based on size
        let sizeMap = ["thumbnail": "50", "small": "100", "medium": "200", "large": "400"]
        let sizeNum = sizeMap[size] ?? "100"
        
        // Note: You'll need the actual image filename from the product data
        return URL(string: "\(baseURL)/products/\(productId)/image_\(sizeNum).jpg")
    }
    
    // MARK: - Search Index
    func fetchSearchIndex(compact: Bool = true) async throws -> SearchIndex {
        let filename = compact ? "search-index-compact.json" : "search-index.json"
        let url = URL(string: "\(baseURL)/\(filename)")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(SearchIndex.self, from: data)
    }
    
    // MARK: - Featured Content
    func fetchFeaturedContent() async throws -> FeaturedContent {
        let url = URL(string: "\(baseURL)/featured-content.json")!
        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(FeaturedContent.self, from: data)
    }
}

// MARK: - Product Detail Model
struct ProductDetail: Codable {
    let productId: String
    let title: String
    let brand: Brand
    let pricing: Pricing
    let rating: Rating
    let media: Media
    let specifications: [String: String]
    
    struct Brand: Codable {
        let name: String
    }
    
    struct Pricing: Codable {
        let currentPrice: Double
    }
    
    struct Rating: Codable {
        let average: Double
        let count: Int
    }
    
    struct Media: Codable {
        let images: [ImageInfo]
        
        struct ImageInfo: Codable {
            let url: String
        }
    }
}

struct FeaturedContent: Codable {
    let sections: [Section]
    let banners: [Banner]
    let quickLinks: [QuickLink]
    
    struct Section: Codable {
        let id: String
        let title: String
        let subtitle: String
        let type: String
        let displayStyle: String
    }
    
    struct Banner: Codable {
        let id: String
        let title: String
        let message: String
    }
    
    struct QuickLink: Codable {
        let title: String
        let categoryId: String
        let color: String
    }
}
```

### 3. SwiftUI Views

```swift
import SwiftUI

// MARK: - Category List View
struct CategoryListView: View {
    @StateObject private var viewModel = CategoryListViewModel()
    
    var body: some View {
        NavigationView {
            List(viewModel.categories) { category in
                NavigationLink(destination: ProductListView(categoryId: category.id)) {
                    HStack {
                        Text(category.name)
                            .font(.headline)
                        Spacer()
                        Text("\(category.productCount)")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .navigationTitle("Categories")
            .task {
                await viewModel.loadCategories()
            }
        }
    }
}

class CategoryListViewModel: ObservableObject {
    @Published var categories: [Category] = []
    
    func loadCategories() async {
        do {
            categories = try await CatalogService.shared.fetchCategories()
        } catch {
            print("Error loading categories: \(error)")
        }
    }
}

// MARK: - Product List View
struct ProductListView: View {
    let categoryId: String
    @StateObject private var viewModel: ProductListViewModel
    
    init(categoryId: String) {
        self.categoryId = categoryId
        _viewModel = StateObject(wrappedValue: ProductListViewModel(categoryId: categoryId))
    }
    
    var body: some View {
        ScrollView {
            LazyVGrid(columns: [GridItem(.adaptive(minimum: 150))], spacing: 16) {
                ForEach(viewModel.products) { product in
                    ProductCard(product: product)
                }
            }
            .padding()
        }
        .navigationTitle(categoryId.capitalized)
        .task {
            await viewModel.loadProducts()
        }
    }
}

class ProductListViewModel: ObservableObject {
    @Published var products: [Product] = []
    let categoryId: String
    
    init(categoryId: String) {
        self.categoryId = categoryId
    }
    
    func loadProducts() async {
        do {
            products = try await CatalogService.shared.fetchProducts(for: categoryId)
        } catch {
            print("Error loading products: \(error)")
        }
    }
}

// MARK: - Product Card
struct ProductCard: View {
    let product: Product
    
    var body: some View {
        VStack(alignment: .leading) {
            AsyncImage(url: CatalogService.shared.imageURL(for: product.productId)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fit)
            } placeholder: {
                ProgressView()
            }
            .frame(height: 150)
            
            VStack(alignment: .leading, spacing: 4) {
                if let brand = product.brand {
                    Text(brand)
                        .font(.caption)
                        .foregroundColor(.orange)
                }
                
                Text(product.name)
                    .font(.subheadline)
                    .lineLimit(2)
                
                if let price = product.price {
                    Text("$\(price, specifier: "%.2f")")
                        .font(.headline)
                        .foregroundColor(.orange)
                }
                
                if let rating = product.rating {
                    HStack(spacing: 2) {
                        Image(systemName: "star.fill")
                            .font(.caption)
                            .foregroundColor(.yellow)
                        Text(String(format: "%.1f", rating))
                            .font(.caption)
                    }
                }
            }
            .padding(8)
        }
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
```

## Caching Strategy

### Recommended TTL (Time To Live)
- **App Config**: 5 minutes (300s)
- **Summary**: 1 hour (3600s)
- **Categories**: 1 hour (3600s)
- **Products**: 24 hours (86400s)
- **Images**: 30 days (2592000s)

### URLCache Configuration

```swift
// Configure URLCache in AppDelegate or App struct
let cacheConfig = URLSessionConfiguration.default
cacheConfig.urlCache = URLCache(
    memoryCapacity: 50_000_000,   // 50 MB
    diskCapacity: 200_000_000,    // 200 MB
    diskPath: "catalog_cache"
)
```

## Offline Mode

1. Download `offline-catalog.json` (14KB) on first launch
2. Cache top 10 products per category
3. Store user favorites locally
4. Sync when connection available

```swift
class OfflineManager {
    func downloadOfflineCatalog() async throws {
        let url = URL(string: "\(baseURL)/offline-catalog.json")!
        let (data, _) = try await URLSession.shared.data(from: url)
        // Save to local storage
        try data.write(to: offlineURL)
    }
}
```

## Deep Linking

### URL Scheme: `orangecatalog://`

```swift
// Handle deep links
func handleDeepLink(_ url: URL) {
    guard url.scheme == "orangecatalog" else { return }
    
    switch url.host {
    case "product":
        if let productId = url.pathComponents.last {
            navigateToProduct(productId)
        }
    case "category":
        if let categoryId = url.pathComponents.last {
            navigateToCategory(categoryId)
        }
    case "search":
        if let query = url.queryParameters["q"] {
            performSearch(query)
        }
    default:
        break
    }
}
```

## Search Implementation

```swift
class SearchManager: ObservableObject {
    @Published var results: [Product] = []
    private var searchIndex: SearchIndex?
    
    func loadSearchIndex() async throws {
        searchIndex = try await CatalogService.shared.fetchSearchIndex(compact: true)
    }
    
    func search(query: String) {
        guard let index = searchIndex else { return }
        
        let keywords = query.lowercased().split(separator: " ").map(String.init)
        var productIds = Set<String>()
        
        for keyword in keywords {
            if let ids = index.keywords[keyword] {
                productIds.formUnion(ids)
            }
        }
        
        results = index.products.filter { productIds.contains($0.id) }
    }
}
```

## Performance Tips

1. **Use compact search index** for mobile (saves 1MB)
2. **Load images progressively** with LazyVGrid/LazyHStack
3. **Implement pagination** for large product lists
4. **Cache aggressively** - data updates infrequently
5. **Prefetch category data** for smooth navigation
6. **Use thumbnail images** in list views (50x50)
7. **Defer loading** of product details until needed

## Testing

```swift
func testCatalogService() async {
    do {
        // Load config
        try await CatalogService.shared.loadConfiguration()
        
        // Fetch categories
        let categories = try await CatalogService.shared.fetchCategories()
        print("✓ Loaded \(categories.count) categories")
        
        // Fetch products
        if let firstCategory = categories.first {
            let products = try await CatalogService.shared.fetchProducts(for: firstCategory.id)
            print("✓ Loaded \(products.count) products")
        }
        
        print("✅ All tests passed!")
    } catch {
        print("❌ Test failed: \(error)")
    }
}
```

## Update Management

Check for updates on app launch:

```swift
func checkForUpdates() async throws {
    let url = URL(string: "\(baseURL)/update-manifest.json")!
    let (data, _) = try await URLSession.shared.data(from: url)
    let manifest = try JSONDecoder().decode(UpdateManifest.self, from: data)
    
    if manifest.currentVersion != currentAppDataVersion {
        // Update available
        if manifest.forceUpdate {
            // Force user to update
        } else {
            // Optional update
        }
    }
}
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/atlanticwaters/Orange-Catalog/issues
- Data updates automatically via GitHub Pages

## License

Product data sourced from The Home Depot. Images and specifications are property of their respective owners.
