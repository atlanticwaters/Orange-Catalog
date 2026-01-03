#!/usr/bin/env python3
"""
Add sample Questions & Answers data to products.
Creates realistic placeholder Q&A for testing layouts.
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta

CATEGORIES_PATH = Path("production data/categories")

# Q&A templates by category
QA_TEMPLATES = {
    "tools": [
        {
            "question": "Does this come with a battery and charger?",
            "answer": "This depends on the specific kit you purchase. The 'tool only' version does not include a battery or charger. The kit version includes both. Please check the product title for details.",
            "askedBy": "DIYDan",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "Is this compatible with my existing batteries?",
            "answer": "Yes, this tool is compatible with all batteries from the same voltage platform. For example, all 20V MAX batteries work with all 20V MAX tools from the same brand.",
            "askedBy": "HomeOwner123",
            "answeredBy": "ToolPro"
        },
        {
            "question": "What is the warranty on this product?",
            "answer": "This product comes with a 3-year limited warranty covering defects in materials and workmanship. Register your product online within 30 days for full coverage.",
            "askedBy": "ContractorMike",
            "answeredBy": "CustomerService"
        },
        {
            "question": "Can this be used for heavy-duty professional work?",
            "answer": "Absolutely. This is designed for professional use and can handle demanding jobsite conditions. The brushless motor provides extended runtime and durability.",
            "askedBy": "ProBuilder",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "How long does the battery last on a single charge?",
            "answer": "Battery life varies by application. Light-duty tasks can see 2-3 hours of use, while heavy-duty applications may use the battery faster. A 5.0Ah battery provides the best runtime.",
            "askedBy": "WeekendWarrior",
            "answeredBy": "ToolPro"
        }
    ],
    "appliances": [
        {
            "question": "Does this require professional installation?",
            "answer": "While DIY installation is possible for those with experience, we recommend professional installation to ensure proper setup and to maintain warranty coverage.",
            "askedBy": "NewHomeowner",
            "answeredBy": "ApplianceExpert"
        },
        {
            "question": "Is this ENERGY STAR certified?",
            "answer": "Yes, this product is ENERGY STAR certified, which means it meets strict energy efficiency guidelines set by the EPA. This can help reduce your utility bills.",
            "askedBy": "EcoConscious",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "What are the dimensions? Will it fit in my space?",
            "answer": "Please refer to the specifications section for exact dimensions. We recommend measuring your space carefully, including door clearance and ventilation requirements.",
            "askedBy": "KitchenReno",
            "answeredBy": "CustomerService"
        },
        {
            "question": "Does this come with a water line for the ice maker?",
            "answer": "No, the water supply line is not included and must be purchased separately. You'll need a standard 1/4-inch water supply line for connection.",
            "askedBy": "FirstTimeBuyer",
            "answeredBy": "InstallPro"
        },
        {
            "question": "How quiet is this appliance?",
            "answer": "This model operates at a low noise level suitable for open floor plans. Check the specifications for the exact decibel rating. Generally, anything under 45 dBA is considered quiet.",
            "askedBy": "QuietHome",
            "answeredBy": "ApplianceExpert"
        }
    ],
    "furniture": [
        {
            "question": "Is assembly required?",
            "answer": "Yes, some assembly is required. All necessary hardware and instructions are included. Most customers complete assembly in 30-60 minutes with basic tools.",
            "askedBy": "ApartmentDweller",
            "answeredBy": "FurnitureExpert"
        },
        {
            "question": "What is the weight capacity?",
            "answer": "Please check the specifications section for the exact weight capacity. Most seating is rated for 250-300 lbs per seat.",
            "askedBy": "SafetyFirst",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "Is the fabric stain-resistant?",
            "answer": "The upholstery is treated with a stain-resistant finish for easy cleaning. For best results, blot spills immediately and clean with a mild soap solution.",
            "askedBy": "ParentOfThree",
            "answeredBy": "CustomerService"
        },
        {
            "question": "Does this come with a warranty?",
            "answer": "Yes, this product includes a 1-year limited warranty against manufacturing defects. Keep your receipt for warranty claims.",
            "askedBy": "SmartShopper",
            "answeredBy": "FurnitureExpert"
        },
        {
            "question": "What tools do I need for assembly?",
            "answer": "You'll need a Phillips head screwdriver and possibly an Allen wrench (usually included). No power tools required, though a cordless drill can speed up assembly.",
            "askedBy": "DIYNewbie",
            "answeredBy": "AssemblyPro"
        }
    ],
    "electrical": [
        {
            "question": "Is this compatible with LED bulbs?",
            "answer": "Yes, this is fully compatible with LED bulbs. For dimmer switches, ensure you use dimmable LED bulbs for best performance.",
            "askedBy": "LEDConvert",
            "answeredBy": "ElectricalPro"
        },
        {
            "question": "Do I need a neutral wire for installation?",
            "answer": "Please check the product specifications. Some smart switches require a neutral wire, while others do not. Most homes built after 1980 have neutral wires.",
            "askedBy": "SmartHomeNewbie",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "Is this compatible with Alexa and Google Home?",
            "answer": "Yes, this product works with Amazon Alexa, Google Assistant, and Apple HomeKit. No hub required - connects directly to your WiFi network.",
            "askedBy": "VoiceControl",
            "answeredBy": "SmartHomePro"
        },
        {
            "question": "Can I install this myself or do I need an electrician?",
            "answer": "If you're comfortable with basic electrical work, this can be a DIY project. Always turn off power at the breaker before working. When in doubt, hire a licensed electrician.",
            "askedBy": "HomeImprover",
            "answeredBy": "ElectricalPro"
        },
        {
            "question": "What is the maximum wattage this can handle?",
            "answer": "Please refer to the specifications for the exact wattage rating. Exceeding the rated wattage can cause overheating and is a safety hazard.",
            "askedBy": "SafetyConscious",
            "answeredBy": "ProductExpert"
        }
    ],
    "home-decor": [
        {
            "question": "Is this item as pictured?",
            "answer": "Yes, the product matches the photos shown. Note that colors may vary slightly due to monitor settings and lighting conditions.",
            "askedBy": "OnlineShopper",
            "answeredBy": "CustomerService"
        },
        {
            "question": "How do I clean this?",
            "answer": "For regular maintenance, dust with a soft, dry cloth. For deeper cleaning, use a slightly damp cloth with mild soap. Avoid harsh chemicals.",
            "askedBy": "CleanFreak",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "Is mounting hardware included?",
            "answer": "Yes, basic mounting hardware is included. For heavy items on drywall, we recommend using wall anchors rated for the item's weight.",
            "askedBy": "WallArtLover",
            "answeredBy": "DecorExpert"
        },
        {
            "question": "Is this suitable for outdoor use?",
            "answer": "This item is designed for indoor use only unless specifically noted as outdoor-rated. Exposure to weather will damage the product.",
            "askedBy": "PatioDecorator",
            "answeredBy": "CustomerService"
        }
    ],
    "storage": [
        {
            "question": "Is this waterproof?",
            "answer": "This container is water-resistant but not fully waterproof. It will protect contents from splashes and light rain but should not be submerged.",
            "askedBy": "GarageOrganizer",
            "answeredBy": "StorageExpert"
        },
        {
            "question": "Can these be stacked?",
            "answer": "Yes, these are designed to stack securely. Check the specifications for the maximum recommended stacking height.",
            "askedBy": "SpaceSaver",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "What is the weight capacity?",
            "answer": "Please refer to the specifications for exact weight limits. Distribute heavy items evenly and don't exceed the recommended capacity.",
            "askedBy": "HeavyLifter",
            "answeredBy": "StorageExpert"
        }
    ],
    "garage": [
        {
            "question": "What is the weight capacity?",
            "answer": "Please check the specifications for the exact weight rating. Always follow the manufacturer's guidelines to ensure safe use.",
            "askedBy": "GaragePro",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "Is assembly required?",
            "answer": "Yes, assembly is required. Instructions and hardware are included. Plan for 1-2 hours for most products.",
            "askedBy": "WeekendProject",
            "answeredBy": "CustomerService"
        },
        {
            "question": "Will this work on uneven garage floors?",
            "answer": "Most products include adjustable leveling feet to compensate for minor floor irregularities. For significantly uneven floors, floor leveling may be needed.",
            "askedBy": "OldGarage",
            "answeredBy": "GarageExpert"
        }
    ],
    "automotive": [
        {
            "question": "Will this fit my vehicle?",
            "answer": "Please check your vehicle's specifications and compare with the product requirements. When in doubt, consult your owner's manual or contact us.",
            "askedBy": "CarOwner",
            "answeredBy": "AutoExpert"
        },
        {
            "question": "Is this easy to install?",
            "answer": "Most automotive accessories are designed for DIY installation. Instructions are included. Some items may require professional installation.",
            "askedBy": "DIYMechanic",
            "answeredBy": "ProductExpert"
        }
    ],
    "default": [
        {
            "question": "What is the return policy?",
            "answer": "This product can be returned within 90 days of purchase with receipt. Items must be in original condition with all packaging and accessories.",
            "askedBy": "CarefulBuyer",
            "answeredBy": "CustomerService"
        },
        {
            "question": "Is this covered by a warranty?",
            "answer": "Yes, this product includes a manufacturer's warranty. Please refer to the warranty section for specific coverage details.",
            "askedBy": "WarrantyWatcher",
            "answeredBy": "ProductExpert"
        },
        {
            "question": "When will this be back in stock?",
            "answer": "Stock availability varies. Sign up for email notifications to be alerted when this item is back in stock.",
            "askedBy": "EagerBuyer",
            "answeredBy": "CustomerService"
        }
    ]
}


def generate_dates():
    """Generate realistic Q&A dates."""
    dates = []
    base_date = datetime.now()

    for i in range(5):
        days_ago = random.randint(7, 365)
        q_date = base_date - timedelta(days=days_ago)
        a_date = q_date + timedelta(days=random.randint(1, 7))
        dates.append({
            "questionDate": q_date.strftime("%Y-%m-%d"),
            "answerDate": a_date.strftime("%Y-%m-%d")
        })

    return dates


def get_qa_for_category(category_path: str) -> list:
    """Get Q&A list for a category."""
    parts = category_path.replace(".json", "").split("/")
    top_category = parts[0] if parts else "default"

    # Get category-specific Q&As
    if top_category in QA_TEMPLATES:
        qa_list = QA_TEMPLATES[top_category]
    else:
        qa_list = QA_TEMPLATES["default"]

    # Generate dates and add helpful counts
    dates = generate_dates()
    result = []

    for i, qa in enumerate(qa_list[:random.randint(2, 4)]):
        entry = {
            "id": f"qa_{i+1}",
            "question": qa["question"],
            "answer": qa["answer"],
            "askedBy": qa["askedBy"],
            "answeredBy": qa["answeredBy"],
            "questionDate": dates[i % len(dates)]["questionDate"],
            "answerDate": dates[i % len(dates)]["answerDate"],
            "helpfulVotes": random.randint(5, 150)
        }
        result.append(entry)

    return result


def main():
    print("=" * 60)
    print("ADDING Q&A DATA TO PRODUCTS")
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

            rel_path = str(json_file.relative_to(CATEGORIES_PATH))
            file_updated = False

            for product in products:
                # Add Q&A if missing
                if not product.get("questionsAndAnswers"):
                    product["questionsAndAnswers"] = get_qa_for_category(rel_path)
                    file_updated = True
                    updated_products += 1

            if file_updated:
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
