# Orange-Catalog Data Format Standardization

## Objective
Standardize all category JSON files to use the full `products` array format instead of the legacy `productIds` format, so the iOS app can display product details for all categories.

## Current State

| Category | File Status | Format | Products |
|----------|-------------|--------|----------|
| appliances | ✅ exists | ✅ products array | 9 |
| automotive | ❌ missing | needs creation | - |
| electrical | ✅ exists | ❌ productIds only | 6 |
| furniture | ✅ exists | ✅ products array | 2 |
| garage | ✅ exists | ❌ productIds only | 5 |
| home-decor | ✅ exists | ❌ productIds only | 4 |
| other | ✅ exists | ✅ products array | 619 |
| storage | ❌ missing | needs creation | - |
| tools | ✅ exists | ✅ products array | 172 |

## Required Changes

### 1. Convert Legacy Categories (electrical, garage, home-decor)

These files currently have this legacy structure:
```json
{
  "categoryId": "electrical",
  "name": "Electrical",
  "productIds": ["100232088", "202019375", ...],
  "totalProducts": 6
}
```

Convert them to the new format matching `tools.json`:
```json
{
  "categoryId": "electrical",
  "name": "Electrical",
  "slug": "electrical",
  "path": "/categories/electrical",
  "version": "1.0",
  "lastUpdated": "2025-12-31T22:30:04.734897",
  "breadcrumbs": [
    { "label": "Home", "url": "/" },
    { "label": "Electrical", "url": "/electrical" }
  ],
  "pageInfo": {
    "totalResults": 6
  },
  "featuredBrands": [],
  "products": [
    {
      "productId": "100232088",
      "modelNumber": "",
      "brand": "Brand Name",
      "title": "Product Title",
      "rating": {
        "average": 4.5,
        "count": 100
      },
      "images": {
        "primary": "https://images.thdstatic.com/productImages/..."
      },
      "badges": [],
      "availability": {
        "inStock": true
      },
      "price": {
        "current": 29.99,
        "currency": "USD"
      }
    }
  ]
}
```

### 2. Create Missing Categories (automotive, storage)

Create new files `automotive.json` and `storage.json` using the same format as above.

You'll need to:
1. Look up the product IDs listed in `categories/index.json` for these categories
2. Fetch product details from `products/{productId}/details.json` files
3. Create the category files with full product data

### 3. Product Object Schema

Each product in the `products` array must have:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| productId | string | ✅ | Unique identifier |
| modelNumber | string | ✅ | Can be empty string |
| brand | string | ✅ | Brand name |
| title | string | ✅ | Product title |
| rating | object | ✅ | `{ average: number, count: number }` |
| images | object | ✅ | `{ primary: "url" }` |
| badges | array | ✅ | Can be empty array |
| availability | object | ✅ | `{ inStock: boolean }` |
| price | object | ✅ | `{ current: number, currency: "USD" }` |

Optional price field for sale items:
```json
"price": {
  "current": 199.00,
  "original": 249.00,
  "currency": "USD"
}
```

### 4. Files to Modify/Create

**Modify:**
- `production data/categories/electrical.json`
- `production data/categories/garage.json`
- `production data/categories/home-decor.json`

**Create:**
- `production data/categories/automotive.json`
- `production data/categories/storage.json`

### 5. Reference Files

Use these existing files as templates:
- `production data/categories/tools.json` - Best example with 172 products
- `production data/categories/appliances.json` - Good example with 9 products

### 6. Validation Checklist

After updating, verify each category file:
- [ ] Has `categoryId`, `name`, `slug`, `path` fields
- [ ] Has `version` and `lastUpdated` fields
- [ ] Has `pageInfo.totalResults` matching products array length
- [ ] Has `products` array (not `productIds`)
- [ ] Each product has all required fields
- [ ] JSON is valid (no trailing commas, proper quoting)

### 7. Update index.json (if needed)

Ensure `categories/index.json` has correct `productCount` values matching the actual number of products in each category file.

---

Once complete, the iOS app will be able to display products for all 9 categories without any "product details not available" errors.
