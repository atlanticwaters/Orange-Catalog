"""
Configuration for Home Depot scraping
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
SCRAPED_DATA_DIR = BASE_DIR / "_scraped data" / "THD Product Page Data"
OUTPUT_DIR = BASE_DIR / "_scraped data" / "Automated Scrapes"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Scraping settings
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 2  # seconds between requests
MAX_RETRIES = 3

# Selenium settings (for JavaScript-heavy pages)
USE_SELENIUM = True  # Set to False to use requests only
HEADLESS_BROWSER = True
PAGE_LOAD_TIMEOUT = 30

# Home Depot URL patterns
HD_BASE_URL = "https://www.homedepot.com"
HD_PLP_PATTERN = "{base}/b/{path}/N-{node_id}"
HD_PIP_PATTERN = "{base}/p/{product_id}"

# Categories to scrape (Tier 1 - High Value)
PRIORITY_CATEGORIES = {
    "appliances": {
        "all": "https://www.homedepot.com/b/Appliances/N-5yc1vZbv1w",
    },
    "refrigerators": {
        "french-door": "https://www.homedepot.com/b/Appliances-Refrigerators-French-Door-Refrigerators/N-5yc1vZc3pi",
        "side-by-side": "https://www.homedepot.com/b/Appliances-Refrigerators-Side-by-Side-Refrigerators/N-5yc1vZc3pk",
        "top-freezer": "https://www.homedepot.com/b/Appliances-Refrigerators-Top-Freezer-Refrigerators/N-5yc1vZc3ol",
        "bottom-freezer": "https://www.homedepot.com/b/Appliances-Refrigerators-Bottom-Freezer-Refrigerators/N-5yc1vZc3oh",
        "freezerless": "https://www.homedepot.com/b/Appliances-Refrigerators-Freezerless-Refrigerators/N-5yc1vZc3of",
    },
    "appliances-specific": {
        "dishwashers": "https://www.homedepot.com/b/Appliances-Dishwashers/N-5yc1vZc3po",
        "ranges": "https://www.homedepot.com/b/Appliances-Ranges/N-5yc1vZc3qb",
        "cooktops": "https://www.homedepot.com/b/Appliances-Cooktops/N-5yc1vZc3pj",
        "wall-ovens": "https://www.homedepot.com/b/Appliances-Wall-Ovens/N-5yc1vZc3r8",
        "washers": "https://www.homedepot.com/b/Appliances-Washers-Dryers-Washers/N-5yc1vZc54q",
        "dryers": "https://www.homedepot.com/b/Appliances-Washers-Dryers-Dryers/N-5yc1vZc54o",
        "microwaves": "https://www.homedepot.com/b/Appliances-Microwaves/N-5yc1vZc3q1",
        "air-conditioners": "https://www.homedepot.com/b/Heating-Venting-Cooling-Air-Conditioners/N-5yc1vZc4m5",
    }
}

# Output settings
SAVE_HTML = True  # Save raw HTML
SAVE_JSON = True  # Save parsed JSON
SAVE_MANIFEST = True  # Save manifest file (like your existing scraped data)
