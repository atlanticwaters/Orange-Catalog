#!/usr/bin/env python3
"""
Generate additional image size variants for iOS app.
Creates thumbnail (50x50), medium (200x200), and large (400x400) versions.
"""

import os
import json
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

def resize_image(input_path, output_path, size, quality=85):
    """Resize image to specified size."""
    try:
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate aspect ratio
            img.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Create a square image with white background
            result = Image.new('RGB', (size, size), (255, 255, 255))
            offset = ((size - img.size[0]) // 2, (size - img.size[1]) // 2)
            result.paste(img, offset)
            
            # Save optimized image
            result.save(output_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False

def process_product_images(product_dir, sizes):
    """Process all images for a product."""
    processed = []
    
    # Find the existing 100x100 image
    images = list(product_dir.glob("*_100.jpg"))
    if not images:
        return processed
    
    source_image = images[0]
    base_name = source_image.stem.replace("_100", "")
    
    for size_name, size_px in sizes.items():
        if size_name == "small":  # Skip, already have 100x100
            continue
        
        output_name = f"{base_name}_{size_px}.jpg"
        output_path = product_dir / output_name
        
        if resize_image(source_image, output_path, size_px):
            processed.append({
                "size": size_name,
                "filename": output_name,
                "dimensions": f"{size_px}x{size_px}"
            })
    
    return processed

def generate_image_variants():
    """Generate all image size variants."""
    
    base_dir = Path(__file__).parent / "production data"
    products_dir = base_dir / "products"
    
    sizes = {
        "thumbnail": 50,
        "small": 100,      # Already exists
        "medium": 200,
        "large": 400
    }
    
    print("Generating image variants...")
    print(f"Sizes: {', '.join([f'{k}={v}x{v}' for k, v in sizes.items()])}")
    
    # Get all product directories
    product_dirs = [d for d in products_dir.iterdir() if d.is_dir()]
    total_products = len(product_dirs)
    
    print(f"Found {total_products} product directories")
    
    results = {
        "version": "1.0.0",
        "generatedAt": datetime.now().isoformat(),
        "sizes": sizes,
        "products": {},
        "statistics": {
            "totalProducts": 0,
            "processedProducts": 0,
            "failedProducts": 0,
            "generatedImages": 0
        }
    }
    
    processed_count = 0
    failed_count = 0
    generated_images = 0
    
    # Process images with thread pool
    max_workers = min(8, os.cpu_count() or 4)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_product = {
            executor.submit(process_product_images, product_dir, sizes): product_dir
            for product_dir in product_dirs
        }
        
        for future in as_completed(future_to_product):
            product_dir = future_to_product[future]
            product_id = product_dir.name
            
            try:
                variants = future.result()
                if variants:
                    results["products"][product_id] = variants
                    processed_count += 1
                    generated_images += len(variants)
                else:
                    failed_count += 1
                
                if (processed_count + failed_count) % 50 == 0:
                    progress = (processed_count + failed_count) / total_products * 100
                    print(f"Progress: {progress:.1f}% ({processed_count + failed_count}/{total_products})")
                    
            except Exception as e:
                print(f"Error processing {product_id}: {e}")
                failed_count += 1
    
    results["statistics"]["totalProducts"] = total_products
    results["statistics"]["processedProducts"] = processed_count
    results["statistics"]["failedProducts"] = failed_count
    results["statistics"]["generatedImages"] = generated_images
    
    # Save results
    output_file = base_dir / "image-variants.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Image variants generated: {output_file}")
    print(f"  - Total products: {total_products}")
    print(f"  - Processed: {processed_count}")
    print(f"  - Failed: {failed_count}")
    print(f"  - Images generated: {generated_images}")
    
    # Calculate total size
    total_size = 0
    for product_dir in products_dir.iterdir():
        if product_dir.is_dir():
            for img in product_dir.glob("*.jpg"):
                total_size += img.stat().st_size
    
    print(f"  - Total image size: {total_size / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    generate_image_variants()
