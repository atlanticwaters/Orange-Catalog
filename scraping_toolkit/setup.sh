#!/bin/bash
# Quick setup script for scraping toolkit

set -e

echo "🛠️  Setting up Home Depot Scraping Toolkit..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start Commands:"
echo ""
echo "   # Test with a single category (10 products)"
echo "   python3 batch_scraper.py --category french-door --scrape-products --limit 10"
echo ""
echo "   # Scrape your existing product IDs (first 50)"
echo "   python3 batch_scraper.py --existing-products --limit 50"
echo ""
echo "   # Scrape all priority categories"
echo "   python3 batch_scraper.py --all-categories"
echo ""
echo "📖 See README.md for full documentation"
echo ""
