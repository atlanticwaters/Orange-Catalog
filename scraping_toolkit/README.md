# Home Depot Scraping Toolkit

⚠️ **IMPORTANT:** Home Depot uses anti-bot protection that blocks automated Selenium scraping. See [SCRAPING_SUMMARY.md](SCRAPING_SUMMARY.md) for full details and alternatives.

## 🎯 **Best Approach: Use What You Have!**

You already have **76 categories** of scraped HTML data! Instead of fighting anti-bot protection:

### Quick Win #1: Process Existing Scraped Data
```bash
cd "/Users/awaters/Documents/GitHub/Orange Catalog"
python3 extract_category_data.py  # Re-run on all your scraped HTML
python3 finalize_production_data.py
```

### Quick Win #2: Scrape Product Details
Product pages are easier to scrape than category pages:
```bash
cd scraping_toolkit
python3 scrape_pip.py --limit 50  # Start with 50 products
```

### Quick Win #3: Manual Browser Scraping
Use browser extensions like [SingleFile](https://github.com/gildas-lormeau/SingleFile) to save pages, then process them.

---

## 📦 What's Included

### Working Scripts
- ✅ **`scrape_pip.py`** - Scrapes individual product pages (works!)
- ✅ **`process_existing_data.py`** - Analyzes your scraped data
- ⚠️ **`scrape_plp.py`** - Category scraper (blocked by anti-bot)
- ⚠️ **`batch_scraper.py`** - Batch orchestrator (limited by PLP issues)

### Configuration
- `config.py` - Settings and category URLs
- `requirements.txt` - Python dependencies
- `setup.sh` - One-command installation

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd scraping_toolkit
./setup.sh
```

Or manually:
```bash
pip3 install selenium webdriver-manager beautifulsoup4 lxml tqdm tenacity requests
```

### 2. Check What You Have

```bash
python3 process_existing_data.py
```

This shows you the 76 categories already scraped and suggests next steps.

### 3. Scrape Product Details (Recommended)

```bash
# Scrape product pages for your existing 2,607 product IDs
python3 scrape_pip.py --limit 100
```

### 4. Try Category Scraping (May Be Blocked)

```bash
# Test with one category
python3 batch_scraper.py --category french-door --limit 10
```

---

## 📊 Data Fields Extracted

### PIP (Product Pages) ✅ Works
- Product name, brand, model
- Pricing (current + original)  
- Ratings & review count
- Product images (multiple angles)
- Description & features
- Detailed specifications
- Dimensions
- Stock status
- Category breadcrumbs

### PLP (Category Pages) ⚠️ Blocked
- Product IDs
- Filter definitions
- Featured brands
- Hero images

---

## 🔧 Advanced Usage

### Scrape Specific Products
```bash
python3 scrape_pip.py --product-ids 206147639 314298606 322003405
```

### Use Existing Product ID List
```bash
# Create a JSON file with product IDs
echo '["206147639", "314298606"]' > my_products.json

# Scrape those products
python3 scrape_pip.py --input-file my_products.json
```

### Extract Product IDs from Production Data
```bash
python3 << 'EOF'
import json
from pathlib import Path

product_ids = []
for f in Path("../production data/categories").rglob("*.json"):
    if f.name != "index.json":
        with open(f) as file:
            data = json.load(file)
            product_ids.extend(data.get('productIds', []))

with open('all_product_ids.json', 'w') as f:
    json.dump(list(set(product_ids)), f)

print(f"Saved {len(set(product_ids))} unique product IDs")
EOF

python3 scrape_pip.py --input-file all_product_ids.json --limit 100
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Rate limiting (be respectful!)
RATE_LIMIT_DELAY = 2  # seconds between requests

# Browser settings  
USE_SELENIUM = True
HEADLESS_BROWSER = True

# Timeouts
REQUEST_TIMEOUT = 30
PAGE_LOAD_TIMEOUT = 30
```

---

## 🚦 Rate Limiting

**Be respectful of Home Depot's servers!**

- Default: 2 seconds between requests
- Always use `--limit` to test with small batches first
- Consider running during off-peak hours
- Product detail scraping is less intensive than category scraping

---

## 🐛 Troubleshooting

### "No product elements found"
- This means anti-bot protection is blocking the scraper
- **Solution:** Use manual browser scraping or process existing HTML

### Missing dependencies
```bash
pip3 install selenium webdriver-manager beautifulsoup4 lxml tqdm tenacity requests
```

### Selenium errors
```bash
# Install Chrome/Chromium
brew install --cask google-chrome  # macOS
```

---

## 📈 Success Strategy

**Phase 1: Maximize Existing Data** (This Week)
1. Re-run extraction on your 76 scraped categories
2. Scrape 100-500 product details
3. Manually save 4-6 key missing categories

**Phase 2: Incremental Growth** (Next Week)  
1. Process manually saved pages
2. Scrape 500 more product details
3. Validate and deploy

**Phase 3: Maintenance** (Ongoing)
1. Periodic manual refresh of key categories
2. Investigate API access
3. Monitor for data quality

---

## 🎓 Key Takeaways

1. ✅ **Your existing 76 scraped categories are valuable!**
2. ✅ **Product detail scraping works better than category scraping**
3. ⚠️ **Anti-bot protection blocks automated category scraping**
4. ✅ **Manual browser scraping is reliable alternative**
5. ✅ **Focus on extracting value from what you have**

---

## 📖 Full Documentation

- [SCRAPING_SUMMARY.md](SCRAPING_SUMMARY.md) - Detailed analysis and recommendations
- [../README.md](../README.md) - Main project documentation
- [../PROJECT_COMPLETE.md](../PROJECT_COMPLETE.md) - Project completion summary

---

## 🤝 Need More Categories?

**Best approach:** Manual browser scraping

1. Install [SingleFile](https://github.com/gildas-lormeau/SingleFile) extension
2. Visit category page on homedepot.com
3. Click extension icon → Save complete page
4. Save to `_scraped data/THD Product Page Data/[Category]/`
5. Run `extract_category_data.py` to process

**High-value targets:**
- French Door Refrigerators
- Side by Side Refrigerators
- Dishwashers (need more products)
- Ranges (need more products)

---

## ✨ Bottom Line

The automated scraping toolkit hits anti-bot protection, but you have great alternatives:

1. **Process your existing 76 categories** ← Start here!
2. **Scrape product details** for your 2,607 IDs  
3. **Manually save** a few key categories

You already have most of the data - now focus on extraction and enhancement! 🎉
