#!/bin/bash
# Generate all iOS app integration data

set -e

echo "🍊 Orange Catalog - iOS App Data Generator"
echo "=========================================="
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"
echo ""

# 1. Generate search index
echo "📚 Generating search index..."
python3 generate_search_index.py
echo ""

# 2. Generate offline catalog
echo "📱 Generating offline catalog..."
python3 generate_offline_catalog.py
echo ""

# 3. Generate image variants (optional - can be slow)
if [ "$1" = "--with-images" ]; then
    echo "🖼️  Generating image variants..."
    if ! command -v pillow &> /dev/null; then
        echo "Installing Pillow for image processing..."
        pip install Pillow
    fi
    python3 generate_image_variants.py
    echo ""
else
    echo "⏭️  Skipping image variants (use --with-images flag to generate)"
    echo ""
fi

# 4. Update timestamps in config files
echo "⏰ Updating timestamps..."
python3 -c "
import json
from datetime import datetime
from pathlib import Path

base_dir = Path('production data')
timestamp = datetime.now().isoformat()

# Update app-config.json
config_file = base_dir / 'app-config.json'
if config_file.exists():
    with open(config_file, 'r') as f:
        config = json.load(f)
    config['lastUpdated'] = timestamp
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f'  ✓ Updated {config_file}')

# Update update-manifest.json
manifest_file = base_dir / 'update-manifest.json'
if manifest_file.exists():
    with open(manifest_file, 'r') as f:
        manifest = json.load(f)
    manifest['lastUpdated'] = timestamp
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f'  ✓ Updated {manifest_file}')
"
echo ""

echo "✅ All iOS app data generated successfully!"
echo ""
echo "Generated files:"
echo "  - production data/app-config.json"
echo "  - production data/search-index.json"
echo "  - production data/search-index-compact.json"
echo "  - production data/offline-catalog.json"
echo "  - production data/featured-content.json"
echo "  - production data/update-manifest.json"
echo "  - production data/deeplink-map.json"
if [ "$1" = "--with-images" ]; then
    echo "  - production data/image-variants.json"
    echo "  - Multiple image size variants (50x50, 200x200, 400x400)"
fi
echo ""
echo "🚀 Ready for iOS app integration!"
