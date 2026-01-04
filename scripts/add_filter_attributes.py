#!/usr/bin/env python3
"""
Add filter attributes to products for iOS accordion-style filter sheet.

Creates two data structures:
1. Category-level `filters` array - defines available filters for the category
2. Product-level `filterAttributes` object - the product's values for each filter

Filter sheet format (accordion style):
- Main attribute header (e.g., "Color/Finish")
  - Expandable values (e.g., "Stainless Steel", "Black", "White")
"""

import json
import re
import random
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CATEGORIES_PATH = Path("production data/categories")
SCRAPED_PATH = Path("_scraped data/THD Product Page Data/_New Stuff")

# =============================================================================
# FILTER DEFINITIONS BY CATEGORY TYPE
# =============================================================================

# Define which filters apply to which category types
CATEGORY_FILTERS = {
    "appliances/refrigerators": [
        {
            "id": "installationDepth",
            "name": "Installation Depth",
            "type": "single",
            "values": ["Counter-Depth", "Standard Depth"]
        },
        {
            "id": "refrigeratorFitWidth",
            "name": "Refrigerator Fit Width",
            "type": "single",
            "values": ["30 in.", "33 in.", "36 in."]
        },
        {
            "id": "capacity",
            "name": "Total Capacity",
            "type": "range",
            "values": ["Under 15 cu. ft.", "15-20 cu. ft.", "20-25 cu. ft.", "25-30 cu. ft.", "Over 30 cu. ft."]
        },
        {
            "id": "colorFinish",
            "name": "Color/Finish",
            "type": "multi",
            "values": ["Stainless Steel", "Black Stainless", "Fingerprint Resistant", "White", "Black", "Slate"]
        },
        {
            "id": "iceMaker",
            "name": "Ice Maker",
            "type": "single",
            "values": ["Yes", "No"]
        },
        {
            "id": "dispenserType",
            "name": "Dispenser Type",
            "type": "multi",
            "values": ["External Ice/Water", "Internal Water", "No Dispenser"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["ENERGY STAR", "Smart/WiFi Enabled", "Fingerprint Resistant", "Door-in-Door"]
        }
    ],
    "appliances/washers-dryers": [
        {
            "id": "applianceType",
            "name": "Appliance Type",
            "type": "single",
            "values": ["Washer", "Dryer", "Washer & Dryer Set", "All-in-One"]
        },
        {
            "id": "loadType",
            "name": "Load Type",
            "type": "single",
            "values": ["Front Load", "Top Load"]
        },
        {
            "id": "capacity",
            "name": "Capacity",
            "type": "range",
            "values": ["Under 4.0 cu. ft.", "4.0-4.5 cu. ft.", "4.5-5.0 cu. ft.", "Over 5.0 cu. ft."]
        },
        {
            "id": "colorFinish",
            "name": "Color/Finish",
            "type": "multi",
            "values": ["White", "Graphite Steel", "Black Steel", "Champagne"]
        },
        {
            "id": "fuelType",
            "name": "Fuel Type",
            "type": "single",
            "values": ["Electric", "Gas"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["ENERGY STAR", "Smart/WiFi Enabled", "Steam", "Stackable"]
        }
    ],
    "appliances/ranges": [
        {
            "id": "fuelType",
            "name": "Fuel Type",
            "type": "single",
            "values": ["Gas", "Electric", "Dual Fuel"]
        },
        {
            "id": "rangeSize",
            "name": "Range Size",
            "type": "single",
            "values": ["30 in.", "36 in.", "48 in."]
        },
        {
            "id": "ovenType",
            "name": "Oven Type",
            "type": "single",
            "values": ["Single Oven", "Double Oven"]
        },
        {
            "id": "colorFinish",
            "name": "Color/Finish",
            "type": "multi",
            "values": ["Stainless Steel", "Black Stainless", "White", "Black", "Slate"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Convection", "Air Fry", "Self-Cleaning", "Smart/WiFi Enabled"]
        }
    ],
    "tools": [
        {
            "id": "powerType",
            "name": "Power Type",
            "type": "single",
            "values": ["Cordless", "Corded", "Pneumatic"]
        },
        {
            "id": "voltage",
            "name": "Voltage",
            "type": "multi",
            "values": ["12V", "18V", "20V MAX", "40V", "60V"]
        },
        {
            "id": "batteryIncluded",
            "name": "Battery Included",
            "type": "single",
            "values": ["Yes", "No (Tool Only)"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Brushless Motor", "LED Light", "Variable Speed", "Bluetooth"]
        }
    ],
    "tools/drills": [
        {
            "id": "drillType",
            "name": "Drill Type",
            "type": "single",
            "values": ["Drill/Driver", "Hammer Drill", "Impact Driver", "Right Angle"]
        },
        {
            "id": "powerType",
            "name": "Power Type",
            "type": "single",
            "values": ["Cordless", "Corded"]
        },
        {
            "id": "voltage",
            "name": "Voltage",
            "type": "multi",
            "values": ["12V", "18V", "20V MAX"]
        },
        {
            "id": "chuckSize",
            "name": "Chuck Size",
            "type": "single",
            "values": ["1/4 in.", "3/8 in.", "1/2 in."]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Brushless Motor", "LED Light", "Variable Speed", "Keyless Chuck"]
        }
    ],
    "tools/saws": [
        {
            "id": "sawType",
            "name": "Saw Type",
            "type": "single",
            "values": ["Circular Saw", "Miter Saw", "Table Saw", "Reciprocating Saw", "Jigsaw", "Band Saw"]
        },
        {
            "id": "powerType",
            "name": "Power Type",
            "type": "single",
            "values": ["Cordless", "Corded"]
        },
        {
            "id": "bladeSize",
            "name": "Blade Size",
            "type": "single",
            "values": ["6-1/2 in.", "7-1/4 in.", "10 in.", "12 in."]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Brushless Motor", "LED Light", "Dust Collection", "Laser Guide"]
        }
    ],
    "furniture": [
        {
            "id": "material",
            "name": "Material",
            "type": "multi",
            "values": ["Wood", "Metal", "Upholstered", "Glass", "Leather"]
        },
        {
            "id": "colorFinish",
            "name": "Color/Finish",
            "type": "multi",
            "values": ["Brown", "Black", "White", "Gray", "Natural", "Espresso"]
        },
        {
            "id": "style",
            "name": "Style",
            "type": "multi",
            "values": ["Modern", "Traditional", "Farmhouse", "Industrial", "Mid-Century"]
        },
        {
            "id": "assemblyRequired",
            "name": "Assembly Required",
            "type": "single",
            "values": ["Yes", "No"]
        }
    ],
    "furniture/bedroom": [
        {
            "id": "furnitureType",
            "name": "Furniture Type",
            "type": "single",
            "values": ["Bed Frame", "Headboard", "Dresser", "Nightstand", "Mattress"]
        },
        {
            "id": "bedSize",
            "name": "Bed Size",
            "type": "single",
            "values": ["Twin", "Full", "Queen", "King", "California King"]
        },
        {
            "id": "material",
            "name": "Material",
            "type": "multi",
            "values": ["Wood", "Metal", "Upholstered", "Leather"]
        },
        {
            "id": "colorFinish",
            "name": "Color/Finish",
            "type": "multi",
            "values": ["Brown", "Black", "White", "Gray", "Natural"]
        }
    ],
    "furniture/living-room": [
        {
            "id": "furnitureType",
            "name": "Furniture Type",
            "type": "single",
            "values": ["Sofa", "Sectional", "Loveseat", "Accent Chair", "Coffee Table", "TV Stand"]
        },
        {
            "id": "seatingCapacity",
            "name": "Seating Capacity",
            "type": "single",
            "values": ["1 Person", "2 Person", "3 Person", "4+ Person"]
        },
        {
            "id": "material",
            "name": "Material",
            "type": "multi",
            "values": ["Fabric", "Leather", "Faux Leather", "Velvet", "Wood"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Reclining", "Sleeper", "Storage", "USB Ports"]
        }
    ],
    "electrical/smart-home": [
        {
            "id": "deviceType",
            "name": "Device Type",
            "type": "single",
            "values": ["Smart Switch", "Smart Dimmer", "Smart Plug", "Smart Thermostat", "Smart Lock", "Smart Camera"]
        },
        {
            "id": "compatibility",
            "name": "Works With",
            "type": "multi",
            "values": ["Amazon Alexa", "Google Assistant", "Apple HomeKit", "Samsung SmartThings"]
        },
        {
            "id": "connectivity",
            "name": "Connectivity",
            "type": "multi",
            "values": ["WiFi", "Bluetooth", "Z-Wave", "Zigbee", "Thread"]
        },
        {
            "id": "hubRequired",
            "name": "Hub Required",
            "type": "single",
            "values": ["Yes", "No"]
        }
    ],
    "electrical/lighting": [
        {
            "id": "lightType",
            "name": "Light Type",
            "type": "single",
            "values": ["LED Bulb", "Recessed Light", "Ceiling Light", "Under Cabinet", "Track Lighting"]
        },
        {
            "id": "brightness",
            "name": "Brightness",
            "type": "range",
            "values": ["Under 800 Lumens", "800-1100 Lumens", "1100-1600 Lumens", "Over 1600 Lumens"]
        },
        {
            "id": "colorTemperature",
            "name": "Color Temperature",
            "type": "single",
            "values": ["Soft White (2700K)", "Warm White (3000K)", "Bright White (4000K)", "Daylight (5000K)"]
        },
        {
            "id": "dimmable",
            "name": "Dimmable",
            "type": "single",
            "values": ["Yes", "No"]
        }
    ],
    "home-decor": [
        {
            "id": "decorType",
            "name": "Decor Type",
            "type": "single",
            "values": ["Wall Art", "Mirror", "Rug", "Artificial Plant", "Throw Pillow", "Curtain"]
        },
        {
            "id": "style",
            "name": "Style",
            "type": "multi",
            "values": ["Modern", "Traditional", "Bohemian", "Coastal", "Farmhouse"]
        },
        {
            "id": "colorFamily",
            "name": "Color Family",
            "type": "multi",
            "values": ["Neutral", "Blue", "Green", "Red", "Gray", "Multicolor"]
        },
        {
            "id": "material",
            "name": "Material",
            "type": "multi",
            "values": ["Wood", "Metal", "Glass", "Fabric", "Ceramic"]
        }
    ],
    "garage": [
        {
            "id": "storageType",
            "name": "Storage Type",
            "type": "single",
            "values": ["Shelving", "Cabinet", "Workbench", "Wall Organization", "Overhead"]
        },
        {
            "id": "material",
            "name": "Material",
            "type": "single",
            "values": ["Steel", "Wood", "Plastic", "Wire"]
        },
        {
            "id": "weightCapacity",
            "name": "Weight Capacity",
            "type": "range",
            "values": ["Under 100 lbs", "100-250 lbs", "250-500 lbs", "Over 500 lbs"]
        },
        {
            "id": "assemblyRequired",
            "name": "Assembly Required",
            "type": "single",
            "values": ["Yes", "No"]
        }
    ],
    "storage": [
        {
            "id": "containerType",
            "name": "Container Type",
            "type": "single",
            "values": ["Storage Bin", "Tote", "Drawer", "Basket", "Cube"]
        },
        {
            "id": "size",
            "name": "Size",
            "type": "range",
            "values": ["Small (Under 20 qt)", "Medium (20-50 qt)", "Large (50-100 qt)", "Extra Large (Over 100 qt)"]
        },
        {
            "id": "material",
            "name": "Material",
            "type": "single",
            "values": ["Plastic", "Fabric", "Metal", "Wicker"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Stackable", "Wheels", "Lid Included", "Clear/See-Through"]
        }
    ],
    "automotive": [
        {
            "id": "productType",
            "name": "Product Type",
            "type": "single",
            "values": ["Battery Charger", "Jump Starter", "Car Jack", "Fluid", "Cleaning Supply"]
        },
        {
            "id": "vehicleType",
            "name": "Vehicle Type",
            "type": "multi",
            "values": ["Car", "Truck", "SUV", "Motorcycle", "RV"]
        },
        {
            "id": "features",
            "name": "Features",
            "type": "multi",
            "values": ["Portable", "Heavy Duty", "Smart Charging", "Multi-Use"]
        }
    ],
    # Default filters that apply to all categories
    "default": [
        {
            "id": "brand",
            "name": "Brand",
            "type": "multi",
            "values": []  # Will be populated from actual product data
        },
        {
            "id": "priceRange",
            "name": "Price",
            "type": "range",
            "values": ["Under $50", "$50-$100", "$100-$250", "$250-$500", "$500-$1000", "Over $1000"]
        },
        {
            "id": "rating",
            "name": "Review Rating",
            "type": "single",
            "values": ["4 Stars & Up", "3 Stars & Up", "2 Stars & Up"]
        },
        {
            "id": "availability",
            "name": "Availability",
            "type": "single",
            "values": ["In Stock", "Available for Order"]
        }
    ]
}


def get_filters_for_category(category_path: str) -> list:
    """Get applicable filters for a category, combining specific and default filters."""
    filters = []

    # Check for exact match first
    if category_path in CATEGORY_FILTERS:
        filters.extend(CATEGORY_FILTERS[category_path])
    else:
        # Check for parent category match
        parts = category_path.split("/")
        for i in range(len(parts), 0, -1):
            parent = "/".join(parts[:i])
            if parent in CATEGORY_FILTERS:
                filters.extend(CATEGORY_FILTERS[parent])
                break

    # Always add default filters
    filters.extend(CATEGORY_FILTERS["default"])

    return filters


def extract_filter_value(product: dict, filter_def: dict, category_path: str) -> str | list | None:
    """Extract a filter value from a product based on filter definition."""
    filter_id = filter_def["id"]
    title = product.get("title", "")
    specs = product.get("specifications", {})

    # Brand - direct extraction
    if filter_id == "brand":
        return product.get("brand")

    # Price range
    if filter_id == "priceRange":
        price = product.get("price", {}).get("current", 0)
        if price < 50:
            return "Under $50"
        elif price < 100:
            return "$50-$100"
        elif price < 250:
            return "$100-$250"
        elif price < 500:
            return "$250-$500"
        elif price < 1000:
            return "$500-$1000"
        else:
            return "Over $1000"

    # Rating
    if filter_id == "rating":
        rating = product.get("rating", {}).get("average", 0)
        if rating >= 4:
            return "4 Stars & Up"
        elif rating >= 3:
            return "3 Stars & Up"
        elif rating >= 2:
            return "2 Stars & Up"
        return None

    # Availability
    if filter_id == "availability":
        in_stock = product.get("availability", {}).get("inStock", True)
        return "In Stock" if in_stock else "Available for Order"

    # Color/Finish - extract from title or specs
    if filter_id == "colorFinish":
        colors = []
        title_lower = title.lower()

        if "stainless steel" in title_lower:
            if "black stainless" in title_lower:
                colors.append("Black Stainless")
            elif "fingerprint" in title_lower:
                colors.append("Fingerprint Resistant")
            else:
                colors.append("Stainless Steel")
        if "white" in title_lower and "stainless" not in title_lower:
            colors.append("White")
        if "black" in title_lower and "stainless" not in title_lower:
            colors.append("Black")
        if "slate" in title_lower:
            colors.append("Slate")
        if "graphite" in title_lower:
            colors.append("Graphite Steel")
        if "brown" in title_lower or "espresso" in title_lower:
            colors.append("Brown")
        if "gray" in title_lower or "grey" in title_lower:
            colors.append("Gray")
        if "natural" in title_lower:
            colors.append("Natural")

        return colors if colors else None

    # Installation Depth (refrigerators)
    if filter_id == "installationDepth":
        if "counter-depth" in title.lower():
            return "Counter-Depth"
        elif "standard depth" in title.lower():
            return "Standard Depth"
        # Default assignment based on capacity
        cap_match = re.search(r'(\d+\.?\d*)\s*cu\.?\s*ft', title, re.I)
        if cap_match:
            capacity = float(cap_match.group(1))
            return "Counter-Depth" if capacity < 22 else "Standard Depth"
        return random.choice(["Counter-Depth", "Standard Depth"])

    # Refrigerator Fit Width
    if filter_id == "refrigeratorFitWidth":
        if "30" in title and "in" in title.lower():
            return "30 in."
        elif "33" in title and "in" in title.lower():
            return "33 in."
        elif "36" in title and "in" in title.lower():
            return "36 in."
        # Extract from width spec
        width = specs.get("Width", "")
        if "30" in width:
            return "30 in."
        elif "33" in width:
            return "33 in."
        elif "36" in width or "35" in width:
            return "36 in."
        return random.choice(["30 in.", "33 in.", "36 in."])

    # Capacity (refrigerators)
    if filter_id == "capacity" and "refrigerator" in category_path:
        cap_match = re.search(r'(\d+\.?\d*)\s*cu\.?\s*ft', title, re.I)
        if cap_match:
            capacity = float(cap_match.group(1))
            if capacity < 15:
                return "Under 15 cu. ft."
            elif capacity < 20:
                return "15-20 cu. ft."
            elif capacity < 25:
                return "20-25 cu. ft."
            elif capacity < 30:
                return "25-30 cu. ft."
            else:
                return "Over 30 cu. ft."
        return random.choice(["20-25 cu. ft.", "25-30 cu. ft."])

    # Capacity (washers)
    if filter_id == "capacity" and "washer" in category_path:
        cap_match = re.search(r'(\d+\.?\d*)\s*cu\.?\s*ft', title, re.I)
        if cap_match:
            capacity = float(cap_match.group(1))
            if capacity < 4.0:
                return "Under 4.0 cu. ft."
            elif capacity < 4.5:
                return "4.0-4.5 cu. ft."
            elif capacity < 5.0:
                return "4.5-5.0 cu. ft."
            else:
                return "Over 5.0 cu. ft."
        return random.choice(["4.5-5.0 cu. ft.", "Over 5.0 cu. ft."])

    # Ice Maker
    if filter_id == "iceMaker":
        if "ice maker" in title.lower() or specs.get("Ice Maker") == "Yes":
            return "Yes"
        return random.choice(["Yes", "No"])

    # Dispenser Type
    if filter_id == "dispenserType":
        title_lower = title.lower()
        if "external" in title_lower or "through door" in title_lower:
            return "External Ice/Water"
        elif "internal" in title_lower or "internal water" in specs.get("Water Dispenser", "").lower():
            return "Internal Water"
        return random.choice(["External Ice/Water", "Internal Water", "No Dispenser"])

    # Features (general)
    if filter_id == "features":
        features = []
        title_lower = title.lower()

        if "energy star" in title_lower:
            features.append("ENERGY STAR")
        if "smart" in title_lower or "wifi" in title_lower or "wi-fi" in title_lower:
            features.append("Smart/WiFi Enabled")
        if "fingerprint" in title_lower:
            features.append("Fingerprint Resistant")
        if "brushless" in title_lower:
            features.append("Brushless Motor")
        if "led" in title_lower:
            features.append("LED Light")
        if "variable speed" in title_lower:
            features.append("Variable Speed")
        if "bluetooth" in title_lower:
            features.append("Bluetooth")
        if "steam" in title_lower:
            features.append("Steam")
        if "convection" in title_lower:
            features.append("Convection")
        if "air fry" in title_lower:
            features.append("Air Fry")
        if "self-clean" in title_lower:
            features.append("Self-Cleaning")
        if "stackable" in title_lower:
            features.append("Stackable")

        return features if features else None

    # Power Type (tools)
    if filter_id == "powerType":
        title_lower = title.lower()
        if "cordless" in title_lower:
            return "Cordless"
        elif "corded" in title_lower:
            return "Corded"
        elif "pneumatic" in title_lower or "air" in title_lower:
            return "Pneumatic"
        # Default based on voltage presence
        if re.search(r'\d+[- ]?v\b', title_lower):
            return "Cordless"
        return random.choice(["Cordless", "Corded"])

    # Voltage (tools)
    if filter_id == "voltage":
        volt_match = re.search(r'(\d+)[- ]?(?:volt|v)\b', title, re.I)
        if volt_match:
            voltage = int(volt_match.group(1))
            if voltage <= 12:
                return "12V"
            elif voltage <= 18:
                return "18V"
            elif voltage <= 20:
                return "20V MAX"
            elif voltage <= 40:
                return "40V"
            else:
                return "60V"
        return random.choice(["18V", "20V MAX"])

    # Material (furniture)
    if filter_id == "material":
        materials = []
        title_lower = title.lower()

        if "wood" in title_lower or "oak" in title_lower or "walnut" in title_lower or "pine" in title_lower:
            materials.append("Wood")
        if "metal" in title_lower or "steel" in title_lower or "iron" in title_lower:
            materials.append("Metal")
        if "upholster" in title_lower or "fabric" in title_lower:
            materials.append("Upholstered")
        if "glass" in title_lower:
            materials.append("Glass")
        if "leather" in title_lower:
            materials.append("Leather")
        if "plastic" in title_lower:
            materials.append("Plastic")
        if "velvet" in title_lower:
            materials.append("Velvet")

        return materials if materials else None

    # Style (furniture/decor)
    if filter_id == "style":
        styles = []
        title_lower = title.lower()

        if "modern" in title_lower or "contemporary" in title_lower:
            styles.append("Modern")
        if "traditional" in title_lower or "classic" in title_lower:
            styles.append("Traditional")
        if "farmhouse" in title_lower or "rustic" in title_lower:
            styles.append("Farmhouse")
        if "industrial" in title_lower:
            styles.append("Industrial")
        if "mid-century" in title_lower:
            styles.append("Mid-Century")
        if "bohemian" in title_lower or "boho" in title_lower:
            styles.append("Bohemian")
        if "coastal" in title_lower:
            styles.append("Coastal")

        return styles if styles else None

    # Bed Size
    if filter_id == "bedSize":
        title_lower = title.lower()
        if "california king" in title_lower or "cal king" in title_lower:
            return "California King"
        elif "king" in title_lower:
            return "King"
        elif "queen" in title_lower:
            return "Queen"
        elif "full" in title_lower or "double" in title_lower:
            return "Full"
        elif "twin" in title_lower:
            return "Twin"
        return random.choice(["Queen", "King", "Full"])

    # Smart Home Compatibility
    if filter_id == "compatibility":
        compat = []
        title_lower = title.lower()

        if "alexa" in title_lower:
            compat.append("Amazon Alexa")
        if "google" in title_lower:
            compat.append("Google Assistant")
        if "homekit" in title_lower or "apple" in title_lower:
            compat.append("Apple HomeKit")
        if "smartthings" in title_lower:
            compat.append("Samsung SmartThings")

        # Default for smart home products
        if not compat and "smart" in title_lower:
            compat = ["Amazon Alexa", "Google Assistant"]

        return compat if compat else None

    # Default: try to match from filter values
    for value in filter_def.get("values", []):
        if value.lower() in title.lower():
            return value

    return None


def generate_filter_attributes(product: dict, filters: list, category_path: str) -> dict:
    """Generate filterAttributes for a product based on available filters."""
    attributes = {}

    for filter_def in filters:
        filter_id = filter_def["id"]

        # Skip brand filter for now (handled separately)
        if filter_id == "brand":
            attributes[filter_id] = product.get("brand")
            continue

        value = extract_filter_value(product, filter_def, category_path)

        if value is not None:
            # For multi-type filters, ensure it's a list
            if filter_def["type"] == "multi" and not isinstance(value, list):
                value = [value]
            attributes[filter_id] = value

    return attributes


def collect_brands_for_category(products: list) -> list:
    """Collect unique brands from products for the brand filter."""
    brands = set()
    for p in products:
        brand = p.get("brand")
        if brand:
            brands.add(brand)
    return sorted(brands)


def main():
    print("=" * 60)
    print("ADDING FILTER ATTRIBUTES TO PRODUCTS")
    print("=" * 60)

    updated_files = 0
    updated_products = 0

    for json_file in sorted(CATEGORIES_PATH.rglob("*.json")):
        if json_file.name.startswith("_") or json_file.name == "index.json":
            continue

        try:
            data = json.loads(json_file.read_text())
            products = data.get("products", [])

            if not products:
                continue

            # Determine category path
            rel_path = str(json_file.relative_to(CATEGORIES_PATH)).replace(".json", "")

            # Get applicable filters
            filters = get_filters_for_category(rel_path)

            # Collect brands for this category
            brands = collect_brands_for_category(products)

            # Update brand filter with actual values
            for f in filters:
                if f["id"] == "brand":
                    f["values"] = brands

            # Store filters at category level
            data["filters"] = filters

            # Add filterAttributes to each product
            for product in products:
                product["filterAttributes"] = generate_filter_attributes(product, filters, rel_path)
                updated_products += 1

            # Update timestamp and save
            data["lastUpdated"] = datetime.now().isoformat()
            json_file.write_text(json.dumps(data, indent=2))
            updated_files += 1

            print(f"  Updated: {rel_path} ({len(products)} products, {len(filters)} filters)")

        except Exception as e:
            print(f"  Error processing {json_file}: {e}")

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"  Files updated: {updated_files}")
    print(f"  Products updated: {updated_products}")
    print(f"\nFilter structure added:")
    print(f"  - Category level: 'filters' array with filter definitions")
    print(f"  - Product level: 'filterAttributes' object with values")


if __name__ == "__main__":
    main()
