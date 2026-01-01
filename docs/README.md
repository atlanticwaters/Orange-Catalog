# Orange Catalog - GitHub Pages

This is the GitHub Pages site for the Orange Catalog project. It provides a web interface to browse the home improvement product catalog.

## Features

- Browse products by category
- Search within categories
- View product details, images, and pricing
- Responsive design for mobile and desktop
- Direct API access to JSON data

## API Endpoints

All data is available as static JSON files:

- **Categories Index**: `/production data/categories/index.json`
- **Category Data**: `/production data/categories/{category-name}.json`
- **Product Details**: `/production data/products/{product-id}/details.json`
- **Product Images**: `/production data/products/{product-id}/{image-filename}.jpg`
- **Summary Stats**: `/production data/SUMMARY.json`

## Usage

Visit the site at: `https://atlanticwaters.github.io/Orange-Catalog/`

### Browse Categories
The home page displays all available product categories with product counts.

### Search
Use the search bar to filter categories or products within a category.

### View Products
Click on any category to see all products in that category with images, pricing, and ratings.

### Access JSON Data
Click on any product or directly access the JSON endpoints to retrieve structured data.

## Data Structure

Each product includes:
- Product ID and name
- Brand information
- Pricing
- Images (100x100px optimized)
- Ratings and reviews
- Category and subcategory
- Specifications and attributes

## Development

The site is built with vanilla HTML, CSS, and JavaScript - no build process required.

Files:
- `index.html` - Main category browser
- `category.html` - Category product listing
- `production data/` - All product data and images

## Data Source

Product data is sourced from The Home Depot and optimized for web delivery.

Last updated: December 31, 2025
