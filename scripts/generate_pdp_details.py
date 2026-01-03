#!/usr/bin/env python3
"""
Generate boilerplate PDP detail data for products.
Creates realistic placeholder data for testing layouts.
"""

import json
import re
from pathlib import Path
from datetime import datetime

CATEGORIES_PATH = Path("production data/categories")

# Boilerplate specifications by category
SPECS_TEMPLATES = {
    "tools": {
        "drills": {
            "description": "Delivers powerful performance for drilling and driving applications. Features a high-efficiency brushless motor for longer runtime and extended tool life. Compact design allows access to tight spaces while the ergonomic grip reduces fatigue during extended use.",
            "specifications": {
                "Power Source": "Cordless",
                "Voltage": "20V MAX",
                "Chuck Size": "1/2 in.",
                "Max Torque": "650 in-lbs",
                "No-Load Speed": "0-2,000 RPM",
                "Battery Included": "Yes",
                "Charger Included": "Yes",
                "Weight": "3.5 lbs"
            },
            "highlights": [
                "Brushless motor delivers up to 57% more runtime",
                "Compact design fits into tight spaces",
                "All-metal transmission for durability",
                "LED light illuminates work area"
            ],
            "warranty": "3-Year Limited Warranty"
        },
        "impact-drivers": {
            "description": "High-torque impact driver designed for driving large fasteners and lag bolts. Brushless motor provides maximum runtime and durability. Three-speed settings allow for greater control over a wide range of applications.",
            "specifications": {
                "Power Source": "Cordless",
                "Voltage": "20V MAX",
                "Drive Size": "1/4 in. hex",
                "Max Torque": "1,825 in-lbs",
                "No-Load Speed": "0-3,250 RPM",
                "Impact Rate": "0-3,600 IPM",
                "Battery Included": "Yes",
                "Weight": "2.8 lbs"
            },
            "highlights": [
                "Delivers 1,825 in-lbs of max torque",
                "3-speed settings for application versatility",
                "Compact design at only 5.3 in. front to back",
                "Built-in LED with 20-second delay"
            ],
            "warranty": "3-Year Limited Warranty"
        },
        "sanders": {
            "description": "Powerful random orbital sander with variable speed control for a wide range of sanding applications. Low-profile design reduces fatigue and allows for extended use. Dust-sealed switch protects against dust ingestion for longer tool life.",
            "specifications": {
                "Power Source": "Cordless",
                "Voltage": "20V MAX",
                "Pad Size": "5 in.",
                "Orbit Diameter": "3/32 in.",
                "Speed": "8,000-12,000 OPM",
                "Dust Collection": "Yes",
                "Weight": "3.2 lbs"
            },
            "highlights": [
                "Variable speed dial for optimal control",
                "Low-profile height reduces fatigue",
                "Hook and loop pad for easy paper changes",
                "Dust-sealed switch extends tool life"
            ],
            "warranty": "3-Year Limited Warranty"
        },
        "saws": {
            "description": "High-performance saw delivers fast, accurate cuts in a variety of materials. Powerful motor and optimized blade design provide smooth cutting performance. Lightweight and ergonomic design reduces user fatigue.",
            "specifications": {
                "Power Source": "Cordless",
                "Voltage": "20V MAX",
                "Blade Diameter": "7-1/4 in.",
                "Bevel Capacity": "57 degrees",
                "Cutting Depth at 90°": "2-9/16 in.",
                "No-Load Speed": "5,200 RPM",
                "Weight": "7.5 lbs"
            },
            "highlights": [
                "Powerful motor for demanding applications",
                "57-degree bevel capacity with stops at 45 and 22.5 degrees",
                "Integrated dust blower keeps line of cut clear",
                "Magnesium shoe for lightweight durability"
            ],
            "warranty": "3-Year Limited Warranty"
        },
        "batteries": {
            "description": "Premium lithium-ion battery pack delivers long runtime and consistent power. State-of-charge LED indicator displays remaining charge. Fuel gauge allows user to monitor charge status.",
            "specifications": {
                "Battery Type": "Lithium-Ion",
                "Voltage": "20V MAX",
                "Amp Hours": "5.0 Ah",
                "Charge Time": "60 minutes",
                "Fuel Gauge": "Yes",
                "Compatible Tools": "All 20V MAX Tools",
                "Weight": "1.4 lbs"
            },
            "highlights": [
                "5.0 Ah capacity for extended runtime",
                "3-LED fuel gauge shows state of charge",
                "No memory effect - charge anytime",
                "Compatible with all 20V MAX tools"
            ],
            "warranty": "3-Year Limited Warranty"
        },
        "grinders": {
            "description": "Powerful angle grinder for grinding, cutting, and surface preparation. High-power motor delivers maximum performance for demanding applications. Tool-free guard adjustment for quick changes.",
            "specifications": {
                "Power Source": "Cordless",
                "Voltage": "20V MAX",
                "Disc Diameter": "4-1/2 in.",
                "Arbor Size": "5/8 in.",
                "No-Load Speed": "9,000 RPM",
                "Spindle Lock": "Yes",
                "Weight": "4.2 lbs"
            },
            "highlights": [
                "High-power motor for demanding applications",
                "Tool-free adjustable guard",
                "2-position side handle for comfort",
                "Quick-Change wheel release"
            ],
            "warranty": "3-Year Limited Warranty"
        },
        "default": {
            "description": "Professional-grade power tool designed for demanding applications. Features durable construction and ergonomic design for comfortable extended use. Backed by industry-leading warranty and service.",
            "specifications": {
                "Power Source": "Cordless",
                "Voltage": "20V MAX",
                "Battery Included": "Yes",
                "Charger Included": "Yes",
                "Weight": "4.0 lbs"
            },
            "highlights": [
                "Professional-grade performance",
                "Durable construction for jobsite use",
                "Ergonomic design reduces fatigue",
                "LED work light for visibility"
            ],
            "warranty": "3-Year Limited Warranty"
        }
    },
    "appliances": {
        "refrigerators": {
            "description": "French door refrigerator with advanced cooling technology keeps food fresh longer. Fingerprint resistant finish reduces smudges and makes cleaning easy. Internal water dispenser provides filtered water without sacrificing door storage.",
            "specifications": {
                "Total Capacity": "27.0 cu. ft.",
                "Refrigerator Capacity": "18.9 cu. ft.",
                "Freezer Capacity": "8.1 cu. ft.",
                "Width": "35-3/4 in.",
                "Height": "69-7/8 in.",
                "Depth": "36-1/4 in.",
                "Ice Maker": "Yes",
                "Water Dispenser": "Internal",
                "Energy Star": "Yes",
                "Annual Energy Cost": "$67"
            },
            "highlights": [
                "Fingerprint resistant stainless steel finish",
                "Internal water dispenser with filter",
                "Full-width temperature-controlled drawer",
                "LED lighting throughout",
                "ENERGY STAR certified"
            ],
            "warranty": "1-Year Limited Warranty"
        },
        "washers-dryers": {
            "description": "High-efficiency washer with advanced wash technology removes tough stains while being gentle on clothes. Smart features allow monitoring and control from your smartphone. Large capacity handles big loads with ease.",
            "specifications": {
                "Capacity": "5.0 cu. ft.",
                "Width": "27 in.",
                "Height": "39 in.",
                "Depth": "31.5 in.",
                "Wash Cycles": "10",
                "Max Spin Speed": "1,300 RPM",
                "Energy Star": "Yes",
                "Smart Features": "WiFi Enabled"
            },
            "highlights": [
                "5.0 cu. ft. mega capacity",
                "TurboWash technology saves time",
                "Steam technology for deep cleaning",
                "Smart diagnosis for easy troubleshooting",
                "ENERGY STAR certified"
            ],
            "warranty": "1-Year Limited Warranty"
        },
        "dishwashers": {
            "description": "Quiet dishwasher with powerful cleaning performance. Multiple wash cycles handle everything from delicate glassware to heavily soiled pots and pans. Third rack provides additional loading flexibility.",
            "specifications": {
                "Capacity": "16 Place Settings",
                "Width": "24 in.",
                "Height": "34 in.",
                "Noise Level": "44 dBA",
                "Wash Cycles": "7",
                "Dry System": "AutoRelease Door",
                "Energy Star": "Yes"
            },
            "highlights": [
                "44 dBA - quiet operation",
                "Third rack for additional capacity",
                "Stainless steel interior tub",
                "Fingerprint resistant finish",
                "AutoRelease door for better drying"
            ],
            "warranty": "1-Year Limited Warranty"
        },
        "default": {
            "description": "Quality home appliance designed for reliable everyday performance. Energy efficient design helps reduce utility costs. Easy-to-use controls and modern styling complement any home.",
            "specifications": {
                "Energy Star": "Yes",
                "Finish": "Stainless Steel",
                "Installation Type": "Built-In"
            },
            "highlights": [
                "ENERGY STAR certified for efficiency",
                "Easy-to-clean stainless steel finish",
                "Intuitive controls",
                "Quiet operation"
            ],
            "warranty": "1-Year Limited Warranty"
        }
    },
    "furniture": {
        "living-room": {
            "description": "Stylish and comfortable furniture piece designed to enhance any living space. Quality construction ensures years of reliable use. Easy assembly with included hardware and instructions.",
            "specifications": {
                "Material": "Solid Wood Frame",
                "Upholstery": "100% Polyester",
                "Weight Capacity": "300 lbs",
                "Assembly Required": "Yes",
                "Indoor/Outdoor": "Indoor Only"
            },
            "highlights": [
                "Solid wood frame construction",
                "Stain-resistant upholstery",
                "Comfortable cushioning",
                "Neutral color complements any decor",
                "Easy assembly"
            ],
            "warranty": "1-Year Limited Warranty"
        },
        "outdoor": {
            "description": "Weather-resistant outdoor furniture built to withstand the elements. Rust-proof frame and UV-resistant materials ensure lasting beauty. Comfortable design perfect for relaxing outdoors.",
            "specifications": {
                "Frame Material": "Powder-Coated Steel",
                "Seat Material": "All-Weather Wicker",
                "Cushion Material": "Olefin Fabric",
                "Weight Capacity": "300 lbs",
                "UV Resistant": "Yes",
                "Assembly Required": "Yes"
            },
            "highlights": [
                "All-weather construction",
                "Rust-resistant powder-coated frame",
                "UV-resistant cushions included",
                "Easy assembly with included tools",
                "Stackable for easy storage"
            ],
            "warranty": "1-Year Limited Warranty"
        },
        "default": {
            "description": "Quality furniture piece designed for comfort and style. Durable construction ensures years of use. Assembly required with included hardware.",
            "specifications": {
                "Material": "Engineered Wood",
                "Assembly Required": "Yes",
                "Indoor/Outdoor": "Indoor Only"
            },
            "highlights": [
                "Durable construction",
                "Modern design",
                "Easy assembly",
                "Versatile styling"
            ],
            "warranty": "1-Year Limited Warranty"
        }
    },
    "electrical": {
        "smart-home": {
            "description": "Smart home device enables convenient control of your home from anywhere. Easy setup connects to your existing WiFi network. Compatible with popular voice assistants for hands-free control.",
            "specifications": {
                "Connectivity": "WiFi 2.4GHz",
                "Voice Control": "Works with Alexa, Google Assistant",
                "App Control": "iOS and Android",
                "Power": "Hardwired",
                "Voltage": "120V"
            },
            "highlights": [
                "Works with Alexa and Google Assistant",
                "Control from anywhere with smartphone app",
                "Easy DIY installation",
                "Schedule and automation features",
                "No hub required"
            ],
            "warranty": "2-Year Limited Warranty"
        },
        "lighting": {
            "description": "Energy-efficient LED lighting provides bright, even illumination. Long-lasting LEDs reduce replacement costs and energy consumption. Multiple mounting options for versatile installation.",
            "specifications": {
                "Lumens": "4,000 lm",
                "Color Temperature": "4000K Cool White",
                "Wattage": "40W",
                "Voltage": "120V",
                "Lifespan": "50,000 hours",
                "Dimmable": "Yes"
            },
            "highlights": [
                "Energy-efficient LED technology",
                "50,000-hour rated lifespan",
                "Instant-on - no warm-up time",
                "Dimmable for adjustable brightness",
                "Easy installation"
            ],
            "warranty": "5-Year Limited Warranty"
        },
        "default": {
            "description": "Quality electrical component for residential or commercial applications. Meets all applicable electrical codes and standards. Professional or DIY installation.",
            "specifications": {
                "Voltage": "120V",
                "Certification": "UL Listed"
            },
            "highlights": [
                "UL Listed for safety",
                "Meets electrical codes",
                "Easy installation",
                "Durable construction"
            ],
            "warranty": "1-Year Limited Warranty"
        }
    },
    "home-decor": {
        "wall-art": {
            "description": "Beautiful wall art adds character and style to any room. Ready to hang with included hardware. Printed on high-quality materials for lasting color.",
            "specifications": {
                "Material": "Canvas on Wood Frame",
                "Mounting": "Ready to Hang",
                "Indoor/Outdoor": "Indoor Only",
                "Cleaning": "Dust with Soft Cloth"
            },
            "highlights": [
                "Ready to hang out of the box",
                "Fade-resistant printing",
                "Lightweight construction",
                "Hardware included"
            ],
            "warranty": "30-Day Return Policy"
        },
        "rugs": {
            "description": "Soft, durable area rug adds warmth and style to any room. Stain-resistant fibers make cleaning easy. Non-slip backing provides stability on hard floors.",
            "specifications": {
                "Material": "100% Polypropylene",
                "Pile Height": "0.5 in.",
                "Backing": "Non-Slip Latex",
                "Stain Resistant": "Yes",
                "Vacuum Safe": "Yes"
            },
            "highlights": [
                "Stain and fade resistant",
                "Non-slip backing included",
                "Easy to clean - vacuum regularly",
                "Soft underfoot",
                "Suitable for high-traffic areas"
            ],
            "warranty": "1-Year Limited Warranty"
        },
        "default": {
            "description": "Quality home decor item designed to enhance your living space. Durable materials ensure lasting beauty. Easy care and maintenance.",
            "specifications": {
                "Indoor/Outdoor": "Indoor Only",
                "Care": "Wipe Clean"
            },
            "highlights": [
                "Quality construction",
                "Stylish design",
                "Easy maintenance",
                "Enhances any room"
            ],
            "warranty": "30-Day Return Policy"
        }
    },
    "storage": {
        "default": {
            "description": "Durable storage solution helps organize your space. Heavy-duty construction handles significant weight. Easy assembly with included hardware.",
            "specifications": {
                "Material": "Heavy-Duty Plastic",
                "Weight Capacity": "200 lbs",
                "Stackable": "Yes",
                "Assembly Required": "No",
                "Indoor/Outdoor": "Both"
            },
            "highlights": [
                "Heavy-duty construction",
                "Stackable design saves space",
                "Weather-resistant",
                "Easy-grip handles",
                "Secure latching lid"
            ],
            "warranty": "Limited Lifetime Warranty"
        }
    },
    "garage": {
        "default": {
            "description": "Professional-grade garage equipment built for demanding use. Durable construction withstands daily wear and tear. Designed for DIY and professional mechanics alike.",
            "specifications": {
                "Material": "Heavy-Duty Steel",
                "Weight Capacity": "500 lbs",
                "Finish": "Powder-Coated",
                "Assembly Required": "Yes"
            },
            "highlights": [
                "Heavy-duty steel construction",
                "Powder-coated for durability",
                "Professional-grade quality",
                "Easy assembly"
            ],
            "warranty": "1-Year Limited Warranty"
        }
    },
    "automotive": {
        "default": {
            "description": "Quality automotive product designed for reliable performance. Meets or exceeds OEM specifications. Easy installation for DIY maintenance.",
            "specifications": {
                "Compatibility": "Universal Fit",
                "Material": "Premium Quality"
            },
            "highlights": [
                "Meets OEM specifications",
                "Easy installation",
                "Quality construction",
                "Reliable performance"
            ],
            "warranty": "1-Year Limited Warranty"
        }
    },
    "default": {
        "default": {
            "description": "Quality product designed for reliable everyday use. Durable construction ensures long-lasting performance. Backed by manufacturer warranty.",
            "specifications": {
                "Quality": "Premium Grade"
            },
            "highlights": [
                "Durable construction",
                "Quality materials",
                "Reliable performance",
                "Easy to use"
            ],
            "warranty": "1-Year Limited Warranty"
        }
    }
}


def get_template_for_product(category_path: str, subcategory: str = None) -> dict:
    """Get the appropriate template based on category path."""
    parts = category_path.replace(".json", "").split("/")
    top_category = parts[0] if parts else "default"
    sub_category = parts[1] if len(parts) > 1 else "default"

    # Try to find matching template
    if top_category in SPECS_TEMPLATES:
        cat_templates = SPECS_TEMPLATES[top_category]
        if sub_category in cat_templates:
            return cat_templates[sub_category]
        elif "default" in cat_templates:
            return cat_templates["default"]

    return SPECS_TEMPLATES["default"]["default"]


def main():
    print("=" * 60)
    print("GENERATING PDP DETAIL DATA")
    print("=" * 60)

    updated_files = 0
    updated_products = 0

    for json_file in CATEGORIES_PATH.rglob("*.json"):
        if json_file.name.startswith("_") or json_file.name == "index.json":
            continue

        try:
            data = json.loads(json_file.read_text())
            products = data.get("products", [])

            if not products:
                continue

            # Get relative path for template lookup
            rel_path = str(json_file.relative_to(CATEGORIES_PATH))
            template = get_template_for_product(rel_path)

            file_updated = False

            for product in products:
                # Add description if missing
                if not product.get("description"):
                    product["description"] = template["description"]
                    file_updated = True

                # Add specifications if missing
                if not product.get("specifications"):
                    product["specifications"] = template["specifications"]
                    file_updated = True

                # Add highlights if missing
                if not product.get("highlights"):
                    product["highlights"] = template["highlights"]
                    file_updated = True

                # Add warranty if missing
                if not product.get("warranty"):
                    product["warranty"] = template["warranty"]
                    file_updated = True

                # Ensure we have a model number (extract from title if possible)
                if not product.get("modelNumber"):
                    # Try to extract from end of title
                    title = product.get("title", "")
                    match = re.search(r'([A-Z0-9]{4,}[-]?[A-Z0-9]*)$', title)
                    if match:
                        product["modelNumber"] = match.group(1)
                    else:
                        product["modelNumber"] = ""
                    file_updated = True

                if file_updated:
                    updated_products += 1

            if file_updated:
                # Update lastUpdated
                data["lastUpdated"] = datetime.now().isoformat()
                json_file.write_text(json.dumps(data, indent=2))
                updated_files += 1
                print(f"  Updated: {rel_path} ({len(products)} products)")

        except Exception as e:
            print(f"  Error processing {json_file}: {e}")

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print("=" * 60)
    print(f"  Files updated: {updated_files}")
    print(f"  Products updated: {updated_products}")


if __name__ == "__main__":
    main()
