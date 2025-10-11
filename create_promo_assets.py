#!/usr/bin/env python3
"""
Generate Chrome Web Store promotional assets.

Requirements:
- Screenshots: 1280x800 or 640x400, JPEG or 24-bit PNG (no alpha)
- Small promo tile: 440x280, JPEG or 24-bit PNG (no alpha)
- Marquee promo tile: 1400x560, JPEG or 24-bit PNG (no alpha)
"""

from PIL import Image, ImageDraw, ImageFont
import os

def convert_screenshot(input_path, output_dir, index):
    """
    Convert screenshot to Chrome Web Store format (1280x800, no alpha).
    """
    print(f"Converting {input_path}...")

    img = Image.open(input_path)

    # Convert RGBA to RGB (remove alpha channel)
    if img.mode == 'RGBA':
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Calculate target size maintaining aspect ratio
    target_width = 1280
    target_height = 800

    # Get current aspect ratio
    aspect_ratio = img.width / img.height
    target_aspect = target_width / target_height

    if aspect_ratio > target_aspect:
        # Image is wider - fit to width
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        # Image is taller - fit to height
        new_height = target_height
        new_width = int(target_height * aspect_ratio)

    # Resize image
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Create canvas and center image
    canvas = Image.new('RGB', (target_width, target_height), (255, 255, 255))
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    canvas.paste(img, (x_offset, y_offset))

    # Save as PNG (24-bit, no alpha)
    output_path = os.path.join(output_dir, f'screenshot-{index}.png')
    canvas.save(output_path, 'PNG', optimize=True)

    print(f"  ✓ Saved: {output_path} ({target_width}x{target_height})")
    return output_path


def create_small_promo_tile(logo_path, output_path):
    """
    Create small promo tile (440x280).
    """
    print("\nCreating small promo tile (440x280)...")

    # Create canvas with green background
    canvas = Image.new('RGB', (440, 280), (34, 139, 34))  # Forest green

    # Load and resize logo
    logo = Image.open(logo_path)
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    # Resize logo to fit nicely (180x180)
    logo_size = 180
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Create a temporary RGB canvas for the logo
    logo_canvas = Image.new('RGB', (logo_size, logo_size), (34, 139, 34))
    logo_canvas.paste(logo, (0, 0), logo)

    # Paste logo (centered horizontally, top third vertically)
    x_pos = (440 - logo_size) // 2
    y_pos = 40
    canvas.paste(logo_canvas, (x_pos, y_pos))

    # Add text using default font
    draw = ImageDraw.Draw(canvas)

    # Title
    title = "Ecomind"
    title_bbox = draw.textbbox((0, 0), title, font=None)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((440 - title_width) // 2, 235), title, fill=(255, 255, 255))

    # Subtitle
    subtitle = "AI Sustainability Tracker"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=None)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((440 - subtitle_width) // 2, 255), subtitle, fill=(240, 240, 240))

    canvas.save(output_path, 'PNG', optimize=True)
    print(f"  ✓ Saved: {output_path}")
    return output_path


def create_marquee_promo_tile(logo_path, output_path):
    """
    Create marquee promo tile (1400x560).
    """
    print("\nCreating marquee promo tile (1400x560)...")

    # Create canvas with gradient-like green background
    canvas = Image.new('RGB', (1400, 560), (34, 139, 34))

    # Load and resize logo
    logo = Image.open(logo_path)
    if logo.mode != 'RGBA':
        logo = logo.convert('RGBA')

    # Resize logo (350x350)
    logo_size = 350
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    # Create RGB version of logo
    logo_canvas = Image.new('RGB', (logo_size, logo_size), (34, 139, 34))
    logo_canvas.paste(logo, (0, 0), logo)

    # Paste logo on left side
    x_pos = 100
    y_pos = (560 - logo_size) // 2
    canvas.paste(logo_canvas, (x_pos, y_pos))

    # Add text
    draw = ImageDraw.Draw(canvas)

    # Main title (larger)
    title = "Ecomind"
    # Simulate larger font by drawing multiple times with offset
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            draw.text((600 + dx, 180 + dy), title, fill=(255, 255, 255))

    # Subtitle
    subtitle = "AI Sustainability Tracker"
    draw.text((600, 240), subtitle, fill=(240, 240, 240))

    # Features
    features = [
        "Track CO2 impact of AI usage",
        "Support 12+ AI providers",
        "Privacy-first design",
        "100% local data storage"
    ]

    y_offset = 290
    for feature in features:
        draw.text((620, y_offset), f"• {feature}", fill=(255, 255, 255))
        y_offset += 30

    canvas.save(output_path, 'PNG', optimize=True)
    print(f"  ✓ Saved: {output_path}")
    return output_path


if __name__ == '__main__':
    print("=" * 60)
    print("Chrome Web Store Promotional Assets Generator")
    print("=" * 60)

    # Create output directory
    output_dir = 'chrome-store-assets'
    os.makedirs(output_dir, exist_ok=True)

    # Convert screenshots
    print("\n[1/3] Converting screenshots to 1280x800...")
    screenshots = [
        'ext-chrome/screenshots/screenshot-1-popup.png',
        'ext-chrome/screenshots/screenshot-2-privacy.png',
        'ext-chrome/screenshots/screenshot-3-providers.png',
        'ext-chrome/screenshots/screenshot-4-environment.png'
    ]

    for i, screenshot in enumerate(screenshots, 1):
        if os.path.exists(screenshot):
            convert_screenshot(screenshot, output_dir, i)
        else:
            print(f"  ⚠ Warning: {screenshot} not found")

    # Create small promo tile
    print("\n[2/3] Creating small promo tile (440x280)...")
    create_small_promo_tile('ecomind_logo.png', f'{output_dir}/small-promo-tile.png')

    # Create marquee promo tile
    print("\n[3/3] Creating marquee promo tile (1400x560)...")
    create_marquee_promo_tile('ecomind_logo.png', f'{output_dir}/marquee-promo-tile.png')

    print("\n" + "=" * 60)
    print("✓ SUCCESS! Generated all promotional assets:")
    print(f"  Screenshots (4): {output_dir}/screenshot-*.png")
    print(f"  Small promo: {output_dir}/small-promo-tile.png")
    print(f"  Marquee promo: {output_dir}/marquee-promo-tile.png")
    print("\nAll assets are ready for Chrome Web Store submission!")
    print("=" * 60)
