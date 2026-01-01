# Orange-Catalog Data Format & Subcategory Filtering

## Overview

This document provides instructions for the Orange-Catalog data agent to enable subcategory filtering in the CameraEye iOS app. The app uses a `DSPLPFilterPanel` component that displays **Style Pills** for subcategory navigation.

---

## Current State

| Category | Products | Subcategories |
|----------|----------|---------------|
| Appliances | 645 | 20 |
| Automotive | 55 | 4 |
| Electrical | 39 | 4 |
| Furniture | 260 | 4 |
| Garage | 167 | 3 |
| Home Decor | 321 | 8 |
| Other | 619 | 0 |
| Storage | 27 | 2 |
| Tools | 899 | 27 |
| **Total** | **3,032** | **72** |

---

## Required Data Changes for Subcategory Filtering

### 1. Add `subcategory` Field to Each Product

Each product in the category JSON files needs a `subcategory` field so the iOS app can filter products by subcategory.

**Current product structure:**
```json
{
  "productId": "320033032",
  "modelNumber": "",
  "brand": "RYOBI",
  "title": "ONE+ 18V Cordless Compact Fixed Base Router (Tool Only)",
  "rating": { "average": 4.6792, "count": 1147 },
  "images": { "primary": "https://images.thdstatic.com/..." },
  "badges": [],
  "availability": { "inStock": true },
  "price": { "current": 79.00, "currency": "USD" }
}
```

**Required product structure (add `subcategory`):**
```json
{
  "productId": "320033032",
  "modelNumber": "",
  "brand": "RYOBI",
  "title": "ONE+ 18V Cordless Compact Fixed Base Router (Tool Only)",
  "subcategory": "Routers",
  "rating": { "average": 4.6792, "count": 1147 },
  "images": { "primary": "https://images.thdstatic.com/..." },
  "badges": [],
  "availability": { "inStock": true },
  "price": { "current": 79.00, "currency": "USD" }
}
```

### 2. Subcategory Naming Requirements

The `subcategory` field value must **exactly match** the subcategory `name` from `index.json` for filtering to work correctly.

**Example from index.json:**
```json
{
  "id": "tools",
  "name": "Tools",
  "slug": "tools",
  "productCount": 899,
  "subcategories": [
    { "id": "air-compressors", "name": "Air Compressors", "slug": "air-compressors", "productCount": 69 },
    { "id": "drills", "name": "Drills", "slug": "drills", "productCount": 32 },
    { "id": "grinders", "name": "Grinders", "slug": "grinders", "productCount": 45 }
  ]
}
```

Products in the Tools category should have:
- `"subcategory": "Air Compressors"` (69 products)
- `"subcategory": "Drills"` (32 products)
- `"subcategory": "Grinders"` (45 products)
- etc.

### 3. Optional: Add Subcategory Image URLs

For visual Style Pills in the iOS app, each subcategory in `index.json` can include an `imageUrl` field:

```json
{
  "id": "french-door",
  "name": "French Door",
  "slug": "french-door",
  "productCount": 76,
  "imageUrl": "https://images.thdstatic.com/productImages/.../french-door-64_100.jpg"
}
```

The iOS app will use this image in the subcategory filter pill.

---

## Complete Product Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `productId` | string | ✅ | Unique identifier |
| `modelNumber` | string | ✅ | Model number (can be empty) |
| `brand` | string | ✅ | Brand name |
| `title` | string | ✅ | Product title |
| `subcategory` | string | ✅ **NEW** | Subcategory name (must match index.json) |
| `rating` | object | ✅ | `{ average: number, count: number }` |
| `images` | object | ✅ | `{ primary: "url" }` |
| `badges` | array | ✅ | Badge strings (can be empty) |
| `availability` | object | ✅ | `{ inStock: boolean }` |
| `price` | object | ✅ | `{ current: number, currency: "USD" }` |

---

## iOS App Integration

The iOS app uses `DSPLPFilterPanel` to display subcategory filters as **Style Pills**:

```swift
// How the iOS app will use subcategory data:

DSPlpFilterPanel(
    title: "TOOLS",
    stylePills: [
        // These are generated from subcategories in index.json
        DSStylePillItem(
            id: "air-compressors",
            text: "Air Compressors",
            imageURL: "https://..."  // Optional subcategory image
        ),
        DSStylePillItem(
            id: "drills",
            text: "Drills",
            imageURL: "https://..."
        ),
        DSStylePillItem(
            id: "grinders",
            text: "Grinders",
            imageURL: "https://..."
        )
    ],
    resultsCount: "899 RESULTS",
    filterPills: [
        DSFilterPillItem(text: "All Filters", icon: Image(systemName: "line.3.horizontal.decrease.circle")),
        DSFilterPillItem(text: "Brand"),
        DSFilterPillItem(text: "Price")
    ],
    onStylePillTap: { item in
        // Filter products where product.subcategory == item.text
        selectedSubcategory = item.text
    }
)
```

When a user taps a Style Pill:
1. App reads the pill's `text` (e.g., "Drills")
2. App filters products: `products.filter { $0.subcategory == "Drills" }`
3. Product list updates to show only matching products

---

## Files to Update

### Category JSON Files

Update each category file in `production data/categories/`:

| File | Products | Subcategories to Tag |
|------|----------|---------------------|
| `appliances.json` | 645 | 20 subcategory values |
| `automotive.json` | 55 | 4 subcategory values |
| `electrical.json` | 39 | 4 subcategory values |
| `furniture.json` | 260 | 4 subcategory values |
| `garage.json` | 167 | 3 subcategory values |
| `home-decor.json` | 321 | 8 subcategory values |
| `other.json` | 619 | 0 (no subcategories) |
| `storage.json` | 27 | 2 subcategory values |
| `tools.json` | 899 | 27 subcategory values |

### Index JSON File

Optionally update `production data/categories/index.json` to add `imageUrl` to each subcategory:

```json
{
  "categories": [
    {
      "id": "appliances",
      "name": "Appliances",
      "slug": "appliances",
      "productCount": 645,
      "subcategories": [
        {
          "id": "refrigerators",
          "name": "Refrigerators",
          "slug": "refrigerators",
          "productCount": 28,
          "imageUrl": "https://images.thdstatic.com/.../refrigerator-64_100.jpg"
        }
      ]
    }
  ]
}
```

---

## Subcategory Reference by Category

### Tools (27 subcategories)
- Air Compressors (69)
- Portable (35)
- Stationary (17)
- Batteries (73)
- Combo Kits (18)
- Drills (32)
- Angle Drills (12)
- Drill Presses (16)
- Hammer Drills (28)
- Grinders (45)
- Impact Drivers (58)
- Impact Wrenches (29)
- Jobsite Radios (6)
- Nailers Staplers (38)
- Oscillating Tools (32)
- Planers (11)
- Polishers (17)
- Power Tool Accessories (67)
- Routers (37)
- Sanders (47)
- Saws (41)
- Circular (35)
- Jigsaws (26)
- Miter (32)
- Reciprocating (30)
- Table (21)
- Woodworking (55)

### Appliances (20 subcategories)
- Air Conditioners (3)
- Beverage Coolers (8)
- Cooktops (4)
- Dishwashers (5)
- Fans (3)
- Floor Care (23)
- Garbage Disposals (16)
- Ice Makers (23)
- Microwaves (8)
- Ranges (29)
- Refrigerators (28)
- Bottom Freezer (29)
- Counter Depth (2)
- Freezerless (16)
- French Door (76)
- Mini Fridges (16)
- Side By Side (31)
- Top Freezer (32)
- Wall Ovens (2)
- Washers Dryers (258)

### Home Decor (8 subcategories)
- Area Rugs (50)
- Blinds (35)
- Curtains (28)
- Lighting (45)
- Mirrors (32)
- Plants (24)
- Throw Pillows (18)
- Wall Art (89)

### Furniture (4 subcategories)
- Bedroom (65)
- Dining (48)
- Living Room (92)
- Office (55)

### Automotive (4 subcategories)
- Car Care (18)
- Jump Starters (12)
- Pressure Washers (15)
- Towing (10)

### Electrical (4 subcategories)
- Batteries (12)
- Extension Cords (8)
- Light Bulbs (11)
- Surge Protectors (8)

### Garage (3 subcategories)
- Garage Doors (45)
- Openers (72)
- Organization (50)

### Storage (2 subcategories)
- Closet (15)
- Shelving (12)

### Other (0 subcategories)
- No subcategories - products don't need `subcategory` field

---

## Validation Checklist

After updating, verify:

- [ ] Each product has a `subcategory` field (except "Other" category)
- [ ] `subcategory` values exactly match names in `index.json`
- [ ] Product counts per subcategory match `index.json` counts
- [ ] JSON is valid (no trailing commas, proper quoting)
- [ ] No duplicate products (same productId appearing twice)
- [ ] Optional: Subcategories in `index.json` have `imageUrl` fields

---

## Example Complete Product

```json
{
  "productId": "320033032",
  "modelNumber": "PCL424B",
  "brand": "RYOBI",
  "title": "ONE+ 18V Cordless Compact Fixed Base Router (Tool Only)",
  "subcategory": "Routers",
  "rating": {
    "average": 4.68,
    "count": 1147
  },
  "images": {
    "primary": "https://images.thdstatic.com/productImages/aa38106e-3feb-413b-afff-422b13e13e47/svn/ryobi-wood-routers-pcl424b-64_100.jpg"
  },
  "badges": ["Top Rated", "Best Seller"],
  "availability": {
    "inStock": true
  },
  "price": {
    "current": 79.00,
    "original": 99.00,
    "currency": "USD"
  }
}
```

---

## Summary

1. **Add `subcategory` field** to every product in category JSON files
2. **Match subcategory names** exactly to `index.json` subcategory names
3. **Optionally add `imageUrl`** to subcategories in `index.json` for visual pills
4. The iOS app's `DSPLPFilterPanel` will render subcategories as tappable Style Pills
5. Tapping a pill filters products by matching `product.subcategory` to the pill text
