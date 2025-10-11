#!/usr/bin/env python3
"""
Generate Chrome Web Store compliant icon from source logo.

Chrome Web Store Requirements:
- 128x128 total canvas
- 96x96 icon content (centered)
- 16px transparent padding on all sides
- PNG with alpha channel
- Works on both light and dark backgrounds
"""

from PIL import Image, ImageFilter, ImageDraw
import sys

def create_chrome_store_icon(input_path, output_path):
    """
    Create a Chrome Web Store compliant icon.

    Args:
        input_path: Path to source logo (e.g., ecomind_logo.png)
        output_path: Path to save compliant icon (e.g., icon128.png)
    """
    print(f"Loading source icon from: {input_path}")

    # Load the source image
    source = Image.open(input_path)

    # Convert to RGBA if not already
    if source.mode != 'RGBA':
        source = source.convert('RGBA')

    print(f"Source image size: {source.size}")

    # Create a new 128x128 transparent canvas
    canvas = Image.new('RGBA', (128, 128), (0, 0, 0, 0))

    # Resize source to 96x96 (leaving 16px padding on all sides)
    icon_size = (96, 96)
    resized = source.resize(icon_size, Image.Resampling.LANCZOS)

    # Calculate position to center the 96x96 icon (16px offset)
    position = (16, 16)

    # Option 1: Keep the green background (with padding)
    # Just paste the resized icon centered
    canvas.paste(resized, position, resized)

    # Add subtle white glow for dark backgrounds
    # Create a glow layer
    glow = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    # Draw white glow around the icon area
    glow_rect = [14, 14, 114, 114]  # Slightly larger than 96x96 content
    glow_draw.rounded_rectangle(glow_rect, radius=12, outline=(255, 255, 255, 40), width=2)

    # Apply slight blur to glow
    glow = glow.filter(ImageFilter.GaussianBlur(radius=1))

    # Composite glow under the icon (for dark backgrounds)
    result = Image.alpha_composite(glow, canvas)

    # Save the result
    print(f"Saving compliant icon to: {output_path}")
    result.save(output_path, 'PNG', optimize=True)

    print(f"✓ Created Chrome Web Store compliant icon:")
    print(f"  - Canvas size: 128x128")
    print(f"  - Icon content: 96x96 (centered)")
    print(f"  - Transparent padding: 16px on all sides")
    print(f"  - Format: PNG with alpha channel")
    print(f"  - Subtle glow for dark background visibility")

    return result


def create_icon_only_version(input_path, output_path):
    """
    Create an icon-only version (no background square).
    Better for working on both light and dark backgrounds.

    Args:
        input_path: Path to source logo
        output_path: Path to save icon-only version
    """
    print(f"\nCreating icon-only version (no background)...")

    source = Image.open(input_path)

    if source.mode != 'RGBA':
        source = source.convert('RGBA')

    # Create transparent canvas
    canvas = Image.new('RGBA', (128, 128), (0, 0, 0, 0))

    # Get pixel data to extract just the white plant icon
    pixels = source.load()
    width, height = source.size

    # Create a new image for just the icon (extract white parts)
    icon_only = Image.new('RGBA', source.size, (0, 0, 0, 0))
    icon_pixels = icon_only.load()

    # Extract the white plant icon (assuming it's white/light colored)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # If pixel is bright (white-ish), keep it
            if (r + g + b) / 3 > 200 and a > 0:
                icon_pixels[x, y] = (255, 255, 255, a)

    # Resize to 96x96
    icon_resized = icon_only.resize((96, 96), Image.Resampling.LANCZOS)

    # Add subtle shadow for light backgrounds
    shadow = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)

    # Draw subtle shadow
    for i in range(3):
        offset = i * 2
        alpha = 30 - i * 10
        shadow_draw.rounded_rectangle(
            [16 + offset, 16 + offset, 112 + offset, 112 + offset],
            radius=8,
            fill=(0, 0, 0, alpha)
        )

    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=2))

    # Paste icon on top of shadow
    canvas = Image.alpha_composite(shadow, canvas)
    canvas.paste(icon_resized, (16, 16), icon_resized)

    # Add white glow for dark backgrounds
    glow = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    glow.paste(icon_resized, (16, 16), icon_resized)

    # Create white outline
    glow_enhanced = glow.filter(ImageFilter.FIND_EDGES)
    glow_enhanced = glow_enhanced.filter(ImageFilter.GaussianBlur(radius=1.5))

    # Composite everything
    result = Image.alpha_composite(canvas, glow_enhanced)

    print(f"Saving icon-only version to: {output_path}")
    result.save(output_path, 'PNG', optimize=True)

    print(f"✓ Created icon-only version (no background)")

    return result


if __name__ == '__main__':
    # Paths
    input_logo = 'ecomind_logo.png'
    output_standard = 'ext-chrome/dist/icons/icon128_compliant.png'
    output_icon_only = 'ext-chrome/dist/icons/icon128_icon_only.png'

    print("=" * 60)
    print("Chrome Web Store Icon Generator")
    print("=" * 60)

    try:
        # Create standard version (with green background + padding)
        print("\n[1/2] Creating standard version (with background)...")
        create_chrome_store_icon(input_logo, output_standard)

        # Create icon-only version (recommended)
        print("\n[2/2] Creating icon-only version (recommended)...")
        create_icon_only_version(input_logo, output_icon_only)

        print("\n" + "=" * 60)
        print("✓ SUCCESS! Generated 2 versions:")
        print(f"  1. {output_standard}")
        print(f"     (Green background with padding)")
        print(f"  2. {output_icon_only}")
        print(f"     (Icon only, works better on both backgrounds)")
        print("\nRecommendation: Use icon-only version for better versatility")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n✗ ERROR: Could not find {input_logo}")
        print(f"  Make sure you run this script from the project root directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)
