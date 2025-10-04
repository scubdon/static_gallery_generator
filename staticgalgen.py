#!/usr/bin/env python3
"""
Static Photo Gallery Generator
Creates a responsive, modern photo gallery from a directory of images.
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def create_thumbnail(image_path, max_size=400):
    """Create a thumbnail and return as base64 data URI"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Calculate thumbnail size maintaining aspect ratio
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Save to bytes
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            buffer.seek(0)
            
            # Convert to base64
            img_data = base64.b64encode(buffer.read()).decode()
            return f"data:image/jpeg;base64,{img_data}"
    except Exception as e:
        print(f"Error creating thumbnail for {image_path}: {e}")
        return None

def get_image_files(directory):
    """Get all image files from directory"""
    images = []
    for file in sorted(Path(directory).iterdir()):
        if file.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file)
    return images

def generate_gallery_html(images, output_dir, title="Photo Gallery"):
    """Generate the HTML gallery page"""
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create images subdirectory
    images_dir = output_path / "images"
    images_dir.mkdir(exist_ok=True)
    
    # Process images
    gallery_items = []
    for idx, img_path in enumerate(images):
        # Copy full-size image
        dest_path = images_dir / img_path.name
        shutil.copy2(img_path, dest_path)
        
        # Create thumbnail
        print(f"Processing {img_path.name}...")
        thumb_data = create_thumbnail(img_path)
        
        if thumb_data:
            gallery_items.append({
                'thumb': thumb_data,
                'full': f"images/{img_path.name}",
                'name': img_path.stem,
                'index': idx
            })
    
    # Generate HTML
    html = generate_html_template(gallery_items, title)
    
    # Write HTML file
    with open(output_path / "index.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n✓ Gallery generated successfully!")
    print(f"  Output: {output_path / 'index.html'}")
    print(f"  Images: {len(gallery_items)}")

def generate_html_template(items, title):
    """Generate the complete HTML template"""
    
    # Generate gallery items HTML
    items_html = "\n".join([
        f'''        <div class="gallery-item" data-index="{item['index']}" onclick="openLightbox({item['index']})">
            <img src="{item['thumb']}" alt="{item['name']}" loading="lazy">
        </div>'''
        for item in items
    ])
    
    # Generate full-size images data
    images_json = "[" + ",".join([
        f'"{item["full"]}"' for item in items
    ]) + "]"
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #0a0a0a;
            color: #fff;
            overflow-x: hidden;
        }}

        header {{
            padding: 2rem;
            text-align: center;
            background: linear-gradient(180deg, #1a1a1a 0%, #0a0a0a 100%);
        }}

        h1 {{
            font-size: 2.5rem;
            font-weight: 300;
            letter-spacing: 0.05em;
        }}

        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            max-width: 1600px;
            margin: 0 auto;
        }}

        .gallery-item {{
            position: relative;
            aspect-ratio: 1;
            overflow: hidden;
            border-radius: 8px;
            cursor: pointer;
            background: #1a1a1a;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .gallery-item:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5);
        }}

        .gallery-item img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}

        .gallery-item:hover img {{
            transform: scale(1.05);
        }}

        /* Lightbox */
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.95);
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .lightbox.active {{
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 1;
        }}

        .lightbox-content {{
            max-width: 90vw;
            max-height: 90vh;
            position: relative;
        }}

        .lightbox-image {{
            max-width: 100%;
            max-height: 90vh;
            object-fit: contain;
            border-radius: 4px;
        }}

        .lightbox-close {{
            position: fixed;
            top: 2rem;
            right: 2rem;
            font-size: 2rem;
            color: #fff;
            cursor: pointer;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            transition: background 0.2s ease;
            z-index: 1001;
        }}

        .lightbox-close:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        .lightbox-nav {{
            position: fixed;
            top: 50%;
            transform: translateY(-50%);
            font-size: 2rem;
            color: #fff;
            cursor: pointer;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            transition: background 0.2s ease;
            z-index: 1001;
        }}

        .lightbox-nav:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}

        .lightbox-prev {{
            left: 2rem;
        }}

        .lightbox-next {{
            right: 2rem;
        }}

        .lightbox-counter {{
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            color: #fff;
            font-size: 0.9rem;
            background: rgba(0, 0, 0, 0.5);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            z-index: 1001;
        }}

        @media (max-width: 768px) {{
            .gallery-grid {{
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 1rem;
                padding: 1rem;
            }}

            h1 {{
                font-size: 1.8rem;
            }}

            .lightbox-nav {{
                width: 40px;
                height: 40px;
                font-size: 1.5rem;
            }}

            .lightbox-prev {{
                left: 1rem;
            }}

            .lightbox-next {{
                right: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
    </header>

    <div class="gallery-grid">
{items_html}
    </div>

    <div class="lightbox" id="lightbox">
        <div class="lightbox-close" onclick="closeLightbox()">×</div>
        <div class="lightbox-nav lightbox-prev" onclick="changeImage(-1)">‹</div>
        <div class="lightbox-nav lightbox-next" onclick="changeImage(1)">›</div>
        <div class="lightbox-content">
            <img class="lightbox-image" id="lightbox-image" src="" alt="">
        </div>
        <div class="lightbox-counter" id="lightbox-counter"></div>
    </div>

    <script>
        const images = {images_json};
        let currentIndex = 0;

        function openLightbox(index) {{
            currentIndex = index;
            showImage();
            const lightbox = document.getElementById('lightbox');
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
        }}

        function closeLightbox() {{
            const lightbox = document.getElementById('lightbox');
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
        }}

        function changeImage(direction) {{
            currentIndex = (currentIndex + direction + images.length) % images.length;
            showImage();
        }}

        function showImage() {{
            const img = document.getElementById('lightbox-image');
            const counter = document.getElementById('lightbox-counter');
            img.src = images[currentIndex];
            counter.textContent = `${{currentIndex + 1}} / ${{images.length}}`;
        }}

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            const lightbox = document.getElementById('lightbox');
            if (!lightbox.classList.contains('active')) return;

            if (e.key === 'Escape') {{
                closeLightbox();
            }} else if (e.key === 'ArrowLeft') {{
                changeImage(-1);
            }} else if (e.key === 'ArrowRight') {{
                changeImage(1);
            }}
        }});

        // Close on background click
        document.getElementById('lightbox').addEventListener('click', (e) => {{
            if (e.target.id === 'lightbox') {{
                closeLightbox();
            }}
        }});
    </script>
</body>
</html>'''

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate a static photo gallery')
    parser.add_argument('input_dir', help='Directory containing images')
    parser.add_argument('-o', '--output', default='gallery', help='Output directory (default: gallery)')
    parser.add_argument('-t', '--title', default='Photo Gallery', help='Gallery title')
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.input_dir):
        print(f"Error: '{args.input_dir}' is not a valid directory")
        return
    
    # Get images
    images = get_image_files(args.input_dir)
    
    if not images:
        print(f"No images found in '{args.input_dir}'")
        return
    
    print(f"Found {len(images)} images")
    
    # Generate gallery
    generate_gallery_html(images, args.output, args.title)

if __name__ == "__main__":
    main()
