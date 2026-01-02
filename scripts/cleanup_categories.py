#!/usr/bin/env python3
"""
Category Cleanup Script for Orange-Catalog

This script identifies and relocates misplaced products across category files.
It ensures:
1. Products are in the correct parent category based on their type
2. Subcategory assignments make sense for the parent category
3. No products are lost during the cleanup process

Usage:
    python scripts/cleanup_categories.py --dry-run    # Preview changes
    python scripts/cleanup_categories.py --apply      # Apply changes
"""

import json
import os
import re
import argparse
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

# Base path for category files
CATEGORIES_PATH = Path("production data/categories")

# Define product classification rules based on title keywords
# Each category has keywords that identify products belonging to it
# More specific patterns should be checked first
CATEGORY_RULES = {
    "appliances": {
        "keywords": [
            r"\brefrigerator\b", r"\bfridge\b", r"\bfreezer\b",
            r"\bwasher\b", r"\bdryer\b", r"\blaundry\b",
            r"\bdishwasher\b", r"\bmicrowave\b",
            r"\boven\b", r"\brange\b(?!\s*hood)", r"\bcooktop\b", r"\bstove\b",
            r"\brange\s*hood\b", r"\bvent\s*hood\b",
            r"\bgarbage\s*disposal\b", r"\bdisposal\b",
            r"\bice\s*maker\b", r"\bbeverage\s*cooler\b", r"\bwine\s*cooler\b",
            r"\bair\s*conditioner\b", r"\bdehumidifier\b", r"\bhumidifier\b",
            r"\bvacuum\b(?!.*seal)", r"\bfloor\s*care\b",
            r"\bcompact\s*kitchen\b",  # Summit Appliance compact kitchens
        ],
        "exclude_keywords": [
            r"\bfaucet\b", r"\bcart\b(?!.*laundry)", r"\bbuffet\b",
            r"\bsideboard\b", r"\barm\s*chair\b", r"\bvelvet\b.*\bchair\b",
            r"\bartificial\b", r"\bplant\b(?!.*air)", r"\bflower\b", r"\bhydrangea\b",
            r"\bwelder\b", r"\bwelding\b",
            r"\btable\s*saw\b", r"\bmiter\s*saw\b", r"\bcircular\s*saw\b",
            r"\bjigsaw\b", r"\bband\s*saw\b", r"\breciprocating\s*saw\b",
            r"\brug\b", r"\bcurtain\b", r"\bmirror\b(?!.*instaview)",
            r"\bmakeup\s*vanity\b", r"\bdressing\s*table\b",
        ],
        "valid_subcategories": [
            "Refrigerators", "French Door", "Side By Side", "Top Freezer",
            "Bottom Freezer", "Mini Fridges", "Freezerless", "Freezers",
            "Washers Dryers", "Dishwashers", "Microwaves",
            "Ranges", "Wall Ovens", "Cooktops", "Range Hoods",
            "Garbage Disposals", "Ice Makers", "Beverage Coolers",
            "Air Conditioners", "Floor Care", "Fans", "Counter Depth",
        ]
    },
    "tools": {
        "keywords": [
            r"\bdrill\b(?!\s*bit)", r"\btable\s*saw\b", r"\bmiter\s*saw\b",
            r"\bcircular\s*saw\b", r"\bjigsaw\b", r"\bband\s*saw\b",
            r"\breciprocating\s*saw\b", r"\bsander\b",
            r"\brouter\b(?!.*wifi)", r"\bgrinder\b", r"\bnailer\b", r"\bnail\s*gun\b",
            r"\bair\s*compressor\b", r"\bwrench\b", r"\bscrewdriver\b",
            r"\bplier\b", r"\blevel\b", r"\btape\s*measure\b",
            r"\btool\s*box\b", r"\btool\s*chest\b", r"\btool\s*storage\b",
            r"\bpower\s*tool\b", r"\bhand\s*tool\b",
            r"\bimpact\s*driver\b", r"\brotary\s*tool\b", r"\boscillating\b",
            r"\bwelder\b", r"\bwelding\b", r"\bsoldering\b",
            r"\bbreaker\s*hammer\b", r"\bdemolition\b",
        ],
        "exclude_keywords": [
            r"\brefrigerator\b", r"\bfridge\b", r"\bmicrowave\b",
            r"\bwasher\b(?!.*pressure)", r"\bdryer\b", r"\bdishwasher\b",
            r"\bvacuum\b",
        ],
        "valid_subcategories": [
            "Power Tools", "Hand Tools", "Power Drills", "Saws",
            "Table Saws", "Miter Saws", "Circular Saws", "Jigsaws",
            "Sanders", "Grinders", "Routers", "Nailers",
            "Impact Drivers", "Impact Wrenches", "Oscillating Tools",
            "Air Compressors", "Tool Storage", "Welding",
        ]
    },
    "home-decor": {
        "keywords": [
            r"\bmirror\b(?!.*instaview)(?!.*refrigerator)",
            r"\brug\b", r"\bcurtain\b", r"\bdrape\b",
            r"\bartificial\b.*\bplant\b", r"\bartificial\b.*\bflower\b",
            r"\bartificial\b.*\bhydrangea\b", r"\bartificial\b.*\barrangement\b",
            r"\bvase\b", r"\bcandle\b", r"\bpicture\s*frame\b", r"\bwall\s*art\b",
            r"\bthrow\s*pillow\b", r"\bdecorative\b",
            r"\bhydrangea\b", r"\bshrub\b", r"\btopiary\b",
        ],
        "exclude_keywords": [
            r"\brefrigerator\b", r"\bfridge\b", r"\boven\b",
            r"\bchair\b", r"\bsofa\b", r"\btable\b", r"\bdesk\b",
        ],
        "valid_subcategories": [
            "Mirrors", "Rugs", "Curtains", "Wall Art", "Artificial Plants",
            "Decorative Accents", "Candles", "Picture Frames",
        ]
    },
    "furniture": {
        "keywords": [
            r"\barm\s*chair\b", r"\baccent\s*chair\b", r"\bvelvet\b.*\bchair\b",
            r"\bsofa\b", r"\bcouch\b", r"\bloveseat\b",
            r"\bdesk\b", r"\bbookcase\b",
            r"\bdresser\b", r"\bbed\b(?!.*truck)(?!.*liner)", r"\bmattress\b",
            r"\bfuton\b", r"\bottoman\b", r"\bbench\b(?!.*work)",
            r"\bsideboard\b", r"\bbuffet\b(?!\s*table)",
            r"\bkitchen\s*cart\b", r"\bbar\s*cart\b", r"\bisland\s*cart\b",
            r"\brolling\b.*\bcart\b",
            r"\bmakeup\s*vanity\b", r"\bdressing\s*table\b",
            r"\bshelving\s*unit\b", r"\bstorage\s*shelf\b",
        ],
        "exclude_keywords": [
            r"\brefrigerator\b", r"\btool\b", r"\bsaw\b",
            r"\bgarage\b",
        ],
        "valid_subcategories": [
            "Chairs", "Sofas", "Tables", "Desks", "Beds",
            "Dressers", "Bookcases", "Cabinets", "Kitchen Carts",
        ]
    },
    "plumbing": {
        "keywords": [
            r"\bfaucet\b", r"\bsink\b(?!.*heat)", r"\btoilet\b",
            r"\bshower\b(?!.*door)", r"\bbathtub\b", r"\btub\b(?!.*wash)",
            r"\bpipe\b(?!.*clamp)", r"\bdrain\b",
            r"\bwater\s*heater\b", r"\bsump\s*pump\b",
        ],
        "exclude_keywords": [
            r"\bgarbage\s*disposal\b",  # disposals are appliances
            r"\bshower\s*door\b",
        ],
        "valid_subcategories": [
            "Faucets", "Kitchen Faucets", "Bathroom Faucets",
            "Sinks", "Toilets", "Showers", "Bathtubs",
            "Water Heaters", "Pipes", "Valves",
        ]
    },
    "bath": {
        "keywords": [
            r"\bbathroom\s*vanity\b", r"\bvanity\b.*\bbathroom\b",
            r"\bshower\s*door\b", r"\bbath\s*accessory\b",
            r"\btowel\s*bar\b", r"\btoilet\s*paper\s*holder\b",
        ],
        "exclude_keywords": [],
        "valid_subcategories": [
            "Bathroom Vanities", "Shower Doors", "Bath Accessories",
        ]
    },
    "lighting": {
        "keywords": [
            r"\bchandelier\b", r"\bpendant\s*light\b",
            r"\bsconce\b", r"\bceiling\s*fan\b", r"\bflush\s*mount\b",
            r"\btrack\s*lighting\b", r"\brecessed\s*light\b",
            r"\blamp\b(?!.*heat)",
        ],
        "exclude_keywords": [
            r"\bwork\s*light\b", r"\bjobsite\b", r"\bflashlight\b",
            r"\bheadlamp\b", r"\btool\b",
        ],
        "valid_subcategories": [
            "Ceiling Lights", "Chandeliers", "Pendant Lights",
            "Wall Sconces", "Lamps", "Ceiling Fans", "Outdoor Lighting",
        ]
    },
    # Keep items in their current category if they belong to these
    "garage": {
        "keywords": [
            r"\bgarage\b", r"\bworkbench\b", r"\bwork\s*table\b",
            r"\btool\s*cabinet\b", r"\bstorage\s*cabinet\b",
        ],
        "exclude_keywords": [],
        "valid_subcategories": [],
    },
    "storage": {
        "keywords": [
            r"\bstorage\b", r"\borganizer\b", r"\bbin\b", r"\btote\b",
        ],
        "exclude_keywords": [
            r"\brefrigerator\b", r"\bfridge\b", r"\bwine\b", r"\bbeverage\b",
        ],
        "valid_subcategories": [],
    },
    "outdoors": {
        "keywords": [
            r"\blawn\s*mower\b", r"\bmower\b", r"\bpush\s*mower\b",
            r"\bstring\s*trimmer\b", r"\bweed\s*eater\b",
            r"\bblower\b", r"\bchainsaw\b", r"\bhedge\s*trimmer\b",
            r"\boutdoor\b", r"\bgarden\b", r"\bpatio\b",
        ],
        "exclude_keywords": [],
        "valid_subcategories": [],
    },
}

# Products that should definitely be excluded from appliances
NON_APPLIANCE_BRANDS = {
    "StyleWell", "HOMESTYLES", "FUFU&GAGA", "US Pride Furniture",
    "NATURAE DECOR", "Lincoln Electric", "KOHLER", "American Standard",
    "Delta", "Moen", "Pfister",  # Faucet brands
    "National Tree Company", "Nearly Natural",  # Artificial plants/decor
}

# Brands that are definitely appliance brands
APPLIANCE_BRANDS = {
    "GE", "LG", "Samsung", "Whirlpool", "Frigidaire", "KitchenAid",
    "Maytag", "Bosch", "Electrolux", "Kenmore", "Amana", "Hotpoint",
    "Haier", "Vissani", "Magic Chef", "Summit Appliance", "ZLINE",
    "Thor Kitchen", "InSinkErator", "Dyson", "Shark", "iRobot",
}


class CategoryCleanup:
    def __init__(self, base_path: Path, dry_run: bool = True):
        self.base_path = base_path
        self.dry_run = dry_run
        self.all_products: Dict[str, dict] = {}  # productId -> product data
        self.product_sources: Dict[str, str] = {}  # productId -> source file
        self.category_files: Dict[str, dict] = {}  # filename -> category data
        self.misplaced_products: List[dict] = []
        self.relocations: List[dict] = []
        self.subcategory_fixes: List[dict] = []

    def load_all_categories(self):
        """Load all category JSON files."""
        print("\n📂 Loading category files...")

        for json_file in self.base_path.rglob("*.json"):
            if json_file.name == "index.json":
                continue

            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if "products" in data and isinstance(data["products"], list):
                    rel_path = str(json_file.relative_to(self.base_path))
                    self.category_files[rel_path] = data

                    for product in data["products"]:
                        product_id = product.get("productId")
                        if product_id:
                            self.all_products[product_id] = product
                            self.product_sources[product_id] = rel_path

            except (json.JSONDecodeError, Exception) as e:
                print(f"  ⚠️  Error loading {json_file}: {e}")

        print(f"  ✅ Loaded {len(self.category_files)} category files")
        print(f"  ✅ Found {len(self.all_products)} total products")

    def classify_product(self, product: dict, current_category: str) -> Optional[str]:
        """Determine the correct category for a product based on its title and brand.

        Returns the suggested category only if we're confident the product is misplaced.
        Returns None if the product should stay in its current category.

        This function is CONSERVATIVE - we only relocate when we're very sure.
        """
        title = product.get("title", "").lower()
        brand = product.get("brand", "")

        # =================================================================
        # PRIORITY 1: Brand-based rules (highest confidence)
        # =================================================================

        # Non-appliance brands that ended up in appliances
        if brand in NON_APPLIANCE_BRANDS and current_category == "appliances":
            # This product definitely shouldn't be in appliances
            # Check for faucets - move to "other" since plumbing.json doesn't have products array
            if re.search(r"\bfaucet\b", title, re.IGNORECASE):
                return "other"
            # Check for furniture items
            if re.search(r"\bcart\b|\bcabinet\b|\bsideboard\b|\bbuffet\b|\bchair\b", title, re.IGNORECASE):
                return "furniture"
            # Default to furniture for known furniture brands
            if brand in {"StyleWell", "HOMESTYLES", "FUFU&GAGA", "US Pride Furniture"}:
                return "furniture"
            # Artificial plants/decor
            if brand == "NATURAE DECOR" or re.search(r"\bartificial\b|\bhydrangea\b|\bplant\b", title, re.IGNORECASE):
                return "home-decor"
            return "other"

        # Appliance brands should be in appliances
        if brand in APPLIANCE_BRANDS and current_category != "appliances":
            # Verify it's actually an appliance
            for keyword in CATEGORY_RULES["appliances"]["keywords"]:
                if re.search(keyword, title, re.IGNORECASE):
                    return "appliances"

        # =================================================================
        # PRIORITY 2: Clear keyword mismatches in appliances
        # =================================================================

        if current_category == "appliances":
            # Skip if it's a known appliance brand - trust the brand
            if brand in APPLIANCE_BRANDS:
                return None

            # These should NEVER be in appliances
            # Note: We move faucets to "other" since plumbing.json doesn't have products array
            # But only if it's actually a faucet product, not a washer with faucet feature
            if re.search(r"\bfaucet\b", title, re.IGNORECASE):
                # Make sure it's actually a faucet, not a washer with "Water Faucet" feature
                if not re.search(r"\bwasher\b|\bdryer\b|\blaundry\b", title, re.IGNORECASE):
                    return "other"
            if re.search(r"\barm\s*chair\b|\bvelvet\s*chair\b|\baccent\s*chair\b", title, re.IGNORECASE):
                return "furniture"
            if re.search(r"\bartificial\b.*\b(plant|flower|hydrangea|arrangement)\b", title, re.IGNORECASE):
                return "home-decor"
            if re.search(r"\bwelder\b|\bwelding\b", title, re.IGNORECASE):
                return "tools"
            if re.search(r"\btable\s*saw\b|\bmiter\s*saw\b|\bcircular\s*saw\b", title, re.IGNORECASE):
                return "tools"
            if re.search(r"\bkitchen\s*cart\b|\brolling\s*cart\b|\bisland\s*cart\b", title, re.IGNORECASE):
                return "furniture"
            if re.search(r"\bbuffet\b|\bsideboard\b", title, re.IGNORECASE):
                return "furniture"

        # =================================================================
        # PRIORITY 3: Appliances in wrong categories
        # =================================================================

        # Wine coolers and beverage coolers are appliances
        if current_category in ("other", "storage") and re.search(
            r"\bwine\s*cooler\b|\bbeverage\s*cooler\b|\bwine\s*cellar\b|\bwine\s*refrigerator\b",
            title, re.IGNORECASE
        ):
            return "appliances"

        # Refrigerators are appliances
        if current_category != "appliances" and re.search(
            r"\brefrigerator\b|\bfreezer\b(?!\s*bag)|\bfridge\b",
            title, re.IGNORECASE
        ):
            return "appliances"

        # =================================================================
        # PRIORITY 4: Tool storage items in garage should stay there
        # =================================================================

        # Don't move garage items - they belong there
        if current_category == "garage":
            return None  # Keep in garage

        # Don't move outdoor items
        if current_category == "outdoors":
            return None

        # Don't move home-decor artificial plants to outdoors
        if current_category == "home-decor":
            return None

        # =================================================================
        # PRIORITY 5: Conservative keyword matching for other categories
        # =================================================================

        # Only do keyword matching for specific problem categories
        if current_category in ("electrical", "other", "storage"):
            # Check if it's clearly a tool
            if re.search(r"\btable\s*saw\b|\bmiter\s*saw\b|\bbreaker\s*hammer\b|\bdemolition\b", title, re.IGNORECASE):
                return "tools"

            # Check if it's clearly furniture
            if re.search(r"\bvanity\s*table\b|\bmakeup\s*vanity\b|\bdressing\s*table\b", title, re.IGNORECASE):
                return "furniture"

        return None

    def get_category_from_path(self, file_path: str) -> str:
        """Extract the main category from a file path."""
        parts = file_path.split("/")
        return parts[0].replace(".json", "") if parts else ""

    def validate_subcategory(self, category: str, subcategory: str, product: dict) -> Optional[str]:
        """Check if a subcategory is valid for a category and suggest corrections."""
        if category not in CATEGORY_RULES:
            return None

        valid_subs = CATEGORY_RULES[category].get("valid_subcategories", [])

        # Check if current subcategory is valid
        if subcategory in valid_subs:
            # Verify the product actually belongs in this subcategory
            title = product.get("title", "").lower()

            if category == "appliances":
                # Check for mismatched appliance subcategories
                if subcategory == "Refrigerators" and not any(
                    re.search(kw, title, re.IGNORECASE)
                    for kw in [r"\brefrigerator\b", r"\bfridge\b", r"\bfreezer\b"]
                ):
                    # Product doesn't seem to be a refrigerator
                    return self._suggest_subcategory(title, category)

                if subcategory == "Ranges" and not any(
                    re.search(kw, title, re.IGNORECASE)
                    for kw in [r"\brange\b", r"\bstove\b", r"\boven\b", r"\bcooktop\b"]
                ):
                    return self._suggest_subcategory(title, category)

            return None  # Valid subcategory

        # Subcategory not in valid list - suggest correction
        return self._suggest_subcategory(product.get("title", ""), category)

    def _suggest_subcategory(self, title: str, category: str) -> Optional[str]:
        """Suggest a subcategory based on product title."""
        title_lower = title.lower()

        if category == "appliances":
            if re.search(r"\bfrench\s*door\b", title_lower):
                return "French Door"
            elif re.search(r"\bside\s*by\s*side\b", title_lower):
                return "Side By Side"
            elif re.search(r"\btop\s*freezer\b", title_lower):
                return "Top Freezer"
            elif re.search(r"\bbottom\s*freezer\b", title_lower):
                return "Bottom Freezer"
            elif re.search(r"\bmini\s*fridge\b|\bcompact\b.*\brefrigerator\b", title_lower):
                return "Mini Fridges"
            elif re.search(r"\bfreezerless\b", title_lower):
                return "Freezerless"
            elif re.search(r"\brefrigerator\b|\bfridge\b", title_lower):
                return "Refrigerators"
            elif re.search(r"\bfreezer\b(?!.*refrigerator)", title_lower):
                return "Freezers"
            elif re.search(r"\bwasher\b|\bdryer\b|\blaundry\b", title_lower):
                return "Washers Dryers"
            elif re.search(r"\bdishwasher\b", title_lower):
                return "Dishwashers"
            elif re.search(r"\bmicrowave\b", title_lower):
                return "Microwaves"
            elif re.search(r"\brange\s*hood\b|\bvent\s*hood\b", title_lower):
                return "Range Hoods"
            elif re.search(r"\bwall\s*oven\b", title_lower):
                return "Wall Ovens"
            elif re.search(r"\bcooktop\b", title_lower):
                return "Cooktops"
            elif re.search(r"\brange\b|\bstove\b", title_lower):
                return "Ranges"
            elif re.search(r"\bgarbage\s*disposal\b|\bdisposal\b", title_lower):
                return "Garbage Disposals"
            elif re.search(r"\bice\s*maker\b", title_lower):
                return "Ice Makers"
            elif re.search(r"\bbeverage\s*cooler\b|\bwine\s*cooler\b", title_lower):
                return "Beverage Coolers"
            elif re.search(r"\bair\s*condition\b", title_lower):
                return "Air Conditioners"
            elif re.search(r"\bvacuum\b|\bfloor\s*care\b", title_lower):
                return "Floor Care"
            elif re.search(r"\bfan\b", title_lower):
                return "Fans"

        return None

    def analyze_misplaced_products(self):
        """Find all products that are in the wrong category."""
        print("\n🔍 Analyzing products for misplacement...")

        for file_path, category_data in self.category_files.items():
            current_category = self.get_category_from_path(file_path)

            for product in category_data.get("products", []):
                product_id = product.get("productId")
                title = product.get("title", "")
                brand = product.get("brand", "")
                subcategory = product.get("subcategory", "")

                # Classify the product - pass current category for comparison
                suggested_category = self.classify_product(product, current_category)

                if suggested_category:
                    self.misplaced_products.append({
                        "productId": product_id,
                        "title": title,
                        "brand": brand,
                        "current_category": current_category,
                        "current_file": file_path,
                        "current_subcategory": subcategory,
                        "suggested_category": suggested_category,
                    })
                else:
                    # Product stays in current category, but check subcategory
                    suggested_sub = self.validate_subcategory(
                        current_category, subcategory, product
                    )
                    if suggested_sub and suggested_sub != subcategory:
                        self.subcategory_fixes.append({
                            "productId": product_id,
                            "title": title,
                            "file": file_path,
                            "current_subcategory": subcategory,
                            "suggested_subcategory": suggested_sub,
                        })

        print(f"  ⚠️  Found {len(self.misplaced_products)} misplaced products")
        print(f"  ⚠️  Found {len(self.subcategory_fixes)} incorrect subcategory assignments")

    def generate_report(self):
        """Generate a detailed report of issues found."""
        print("\n" + "="*80)
        print("📊 CATEGORY CLEANUP REPORT")
        print("="*80)

        if self.misplaced_products:
            print(f"\n🔴 MISPLACED PRODUCTS ({len(self.misplaced_products)} items)")
            print("-"*80)

            # Group by current category
            by_category = defaultdict(list)
            for p in self.misplaced_products:
                by_category[p["current_category"]].append(p)

            for category, products in sorted(by_category.items()):
                print(f"\n  📁 In '{category}' but should be elsewhere:")
                for p in products[:10]:  # Show first 10
                    print(f"      • [{p['brand']}] {p['title'][:60]}...")
                    print(f"        → Should be in: {p['suggested_category']}")
                if len(products) > 10:
                    print(f"      ... and {len(products) - 10} more")

        if self.subcategory_fixes:
            print(f"\n🟡 INCORRECT SUBCATEGORIES ({len(self.subcategory_fixes)} items)")
            print("-"*80)

            # Group by file
            by_file = defaultdict(list)
            for p in self.subcategory_fixes:
                by_file[p["file"]].append(p)

            for file_path, products in sorted(by_file.items()):
                print(f"\n  📄 In '{file_path}':")
                for p in products[:5]:  # Show first 5
                    print(f"      • {p['title'][:50]}...")
                    print(f"        Current: '{p['current_subcategory']}' → Suggested: '{p['suggested_subcategory']}'")
                if len(products) > 5:
                    print(f"      ... and {len(products) - 5} more")

        # Summary statistics
        print("\n" + "="*80)
        print("📈 SUMMARY")
        print("="*80)
        print(f"  Total category files: {len(self.category_files)}")
        print(f"  Total products: {len(self.all_products)}")
        print(f"  Misplaced products: {len(self.misplaced_products)}")
        print(f"  Incorrect subcategories: {len(self.subcategory_fixes)}")

    def apply_fixes(self):
        """Apply the fixes to the category files."""
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made")
            return

        print("\n🔧 Applying fixes...")

        # Track changes for each file
        file_changes: Dict[str, dict] = {}
        products_to_remove: Dict[str, Set[str]] = defaultdict(set)
        products_to_add: Dict[str, List[dict]] = defaultdict(list)

        # Categories that have full product data (not just productIds)
        categories_with_products = {
            self.get_category_from_path(fp) for fp in self.category_files.keys()
        }

        # Process misplaced products
        for mp in self.misplaced_products:
            source_file = mp["current_file"]
            product_id = mp["productId"]
            target_category = mp["suggested_category"]

            # Mark for removal from source
            products_to_remove[source_file].add(product_id)

            # Get the product data
            product = self.all_products.get(product_id)
            if product:
                # Update subcategory for the target category
                suggested_sub = self._suggest_subcategory(
                    product.get("title", ""), target_category
                )
                if suggested_sub:
                    product = product.copy()
                    product["subcategory"] = suggested_sub

                # Check if target category has a products array file
                target_file = f"{target_category}.json"
                if target_category not in categories_with_products:
                    # Target category doesn't have full product data, put in "other"
                    print(f"  ⚠️  Target '{target_category}' doesn't support products array, redirecting to 'other'")
                    target_file = "other.json"
                    # Keep original subcategory info in a note
                    product = product.copy()
                    product["_original_target"] = target_category

                products_to_add[target_file].append(product)

        # Process subcategory fixes
        subcategory_updates: Dict[str, Dict[str, str]] = defaultdict(dict)
        for sf in self.subcategory_fixes:
            file_path = sf["file"]
            product_id = sf["productId"]
            new_subcategory = sf["suggested_subcategory"]
            subcategory_updates[file_path][product_id] = new_subcategory

        # Apply changes to files
        files_modified = set()

        for file_path, data in self.category_files.items():
            modified = False

            # Remove misplaced products
            if file_path in products_to_remove:
                original_count = len(data["products"])
                data["products"] = [
                    p for p in data["products"]
                    if p.get("productId") not in products_to_remove[file_path]
                ]
                if len(data["products"]) != original_count:
                    modified = True
                    print(f"  ➖ Removed {original_count - len(data['products'])} products from {file_path}")

            # Add relocated products
            if file_path in products_to_add:
                data["products"].extend(products_to_add[file_path])
                modified = True
                print(f"  ➕ Added {len(products_to_add[file_path])} products to {file_path}")

            # Fix subcategories
            if file_path in subcategory_updates:
                for product in data["products"]:
                    pid = product.get("productId")
                    if pid in subcategory_updates[file_path]:
                        product["subcategory"] = subcategory_updates[file_path][pid]
                        modified = True

            # Update metadata
            if modified:
                data["lastUpdated"] = datetime.now().isoformat()
                data["pageInfo"]["totalResults"] = len(data["products"])
                files_modified.add(file_path)

                # Write the file
                full_path = self.base_path / file_path
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Modified {len(files_modified)} files")

    def verify_no_products_lost(self):
        """Verify that no products were lost during the cleanup."""
        print("\n🔍 Verifying product counts...")

        # Reload all products
        new_products = set()
        for json_file in self.base_path.rglob("*.json"):
            if json_file.name == "index.json":
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if "products" in data:
                    for product in data["products"]:
                        new_products.add(product.get("productId"))
            except:
                pass

        original_ids = set(self.all_products.keys())

        lost = original_ids - new_products
        gained = new_products - original_ids

        if lost:
            print(f"  ❌ LOST {len(lost)} products!")
            for pid in list(lost)[:5]:
                print(f"      • {pid}")
        else:
            print(f"  ✅ No products lost")

        if gained:
            print(f"  ℹ️  {len(gained)} duplicate products consolidated")

        print(f"  📊 Original: {len(original_ids)} | Final: {len(new_products)}")

        return len(lost) == 0


def main():
    parser = argparse.ArgumentParser(description="Clean up category data")
    parser.add_argument("--dry-run", action="store_true",
                       help="Preview changes without applying them")
    parser.add_argument("--apply", action="store_true",
                       help="Apply the changes")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Please specify --dry-run or --apply")
        return

    # Find the base path
    base_path = Path("production data/categories")
    if not base_path.exists():
        # Try from script location
        script_dir = Path(__file__).parent.parent
        base_path = script_dir / "production data" / "categories"

    if not base_path.exists():
        print(f"❌ Could not find categories path: {base_path}")
        return

    print(f"📂 Working with: {base_path.absolute()}")

    cleanup = CategoryCleanup(base_path, dry_run=args.dry_run)
    cleanup.load_all_categories()
    cleanup.analyze_misplaced_products()
    cleanup.generate_report()

    if args.apply:
        cleanup.apply_fixes()
        cleanup.verify_no_products_lost()
    else:
        print("\n💡 Run with --apply to make these changes")


if __name__ == "__main__":
    main()
