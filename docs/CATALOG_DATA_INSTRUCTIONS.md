# Orange-Catalog Data Format Standardization

## Objective
Standardize all category JSON files to include ALL products from subcategories, so the iOS app can display complete product listings for each top-level category.

## CRITICAL ISSUE: Missing Subcategory Products

Categories currently only have their direct products, but subcategory products are missing. For example:

**Appliances:**
- Current: 9 products
- Expected: 621 products (9 direct + 612 from subcategories)

The `index.json` shows subcategories with their product counts, but these products are NOT included in the parent category files.

## Subcategory Products to Include

### Appliances (currently 9, should be 621)
Include all products from:
- Air Conditioners: 3 products
- Beverage Coolers: 8 products
- Cooktops: 4 products
- Dishwashers: 5 products
- Fans: 3 products
- Floor Care: 23 products
- Garbage Disposals: 16 products
- Ice Makers: 23 products
- Microwaves: 8 products
- Ranges: 29 products
- Refrigerators: 28 products
- Bottom Freezer: 29 products
- Counter Depth: 2 products
- Freezerless: 16 products
- French Door: 76 products
- Mini Fridges: 16 products
- Side By Side: 31 products
- Top Freezer: 32 products
- Wall Ovens: 2 products
- Washers Dryers: 258 products

### Check All Other Categories
Review each category in `index.json` for subcategories and ensure ALL subcategory products are included in the parent category's `products` array.

## Required Actions

### 1. For Each Category with Subcategories:
1. Identify all subcategories listed in `index.json`
2. Gather all product data from subcategory product files
3. Add ALL subcategory products to the parent category's `products` array
4. Update `pageInfo.totalResults` to reflect the true total

### 2. Product Object Schema

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

Example product:
```json
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
```

### 3. Category File Structure

Each category JSON file should have:
```json
{
  "categoryId": "appliances",
  "name": "Appliances",
  "slug": "appliances",
  "path": "/categories/appliances",
  "version": "1.0",
  "lastUpdated": "2025-12-31T22:30:04.734897",
  "pageInfo": {
    "totalResults": 621
  },
  "featuredBrands": [],
  "products": [
    // ALL 621 products here
  ]
}
```

### 4. Files to Update

| Category | Current | Expected | Action |
|----------|---------|----------|--------|
| appliances | 9 | 621 | Add 612 subcategory products |
| automotive | 55 | ? | Check for missing subcategories |
| electrical | 39 | ? | Check for missing subcategories |
| furniture | 2 | ? | Check for missing subcategories |
| garage | 167 | ? | Check for missing subcategories |
| home-decor | 156 | ? | Check for missing subcategories |
| other | 619 | ? | Check for missing subcategories |
| storage | 27 | ? | Check for missing subcategories |
| tools | 172 | ? | Check for missing subcategories |

### 5. Validation Checklist

After updating, verify each category file:
- [ ] `pageInfo.totalResults` matches `products` array length
- [ ] ALL subcategory products are included
- [ ] Each product has all required fields
- [ ] JSON is valid (no trailing commas, proper quoting)
- [ ] No duplicate products (same productId appearing twice)

### 6. Update index.json

Update `categories/index.json` so the `productCount` for each category matches the actual number of products in that category's JSON file.

---

## Summary

The main issue is that **subcategory products are not being included in the parent category files**. The iOS app loads products from `categories/{slug}.json` and expects ALL products for that category to be in the `products` array.

Please iterate through each category, identify its subcategories from `index.json`, and add all subcategory products to the parent category file.
