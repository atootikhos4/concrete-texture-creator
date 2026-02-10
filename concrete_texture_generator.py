#!/usr/bin/env python3
"""
Concrete Texture Generator

Generates realistic concrete textures with natural imperfections including:
- Base color fill
- Perlin/Simplex noise for tonal variation
- Fine grain/sand texture
- Speckles & aggregate spots
- Micro-cracks/hairline fractures
- Surface pores/pinholes
- Subtle color variation/staining
- Dust/light surface haze
"""

import argparse
import random
import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from opensimplex import OpenSimplex


# Concrete color presets extracted/inspired by reference images
# Mix of extracted colors and realistic concrete tones
CONCRETE_PALETTE = {
    1: {'name': 'Dark Gray', 'color': '#4e4e54'},
    2: {'name': 'Medium Gray', 'color': '#54545c'},
    3: {'name': 'Slate Gray', 'color': '#52525a'},
    4: {'name': 'Charcoal', 'color': '#3e3c3f'},
    5: {'name': 'Light Cement', 'color': '#b5a898'},
    6: {'name': 'Classic Concrete', 'color': '#8c8680'},
    7: {'name': 'Warm Beige', 'color': '#c4b5a0'},
    8: {'name': 'Cool Gray', 'color': '#9b9b9b'},
    9: {'name': 'Weathered Gray', 'color': '#a8a39e'},
    10: {'name': 'Stone Gray', 'color': '#979288'},
    11: {'name': 'Sandy Concrete', 'color': '#d4c8b8'},
    12: {'name': 'Dusty Gray', 'color': '#b8b0a8'},
}


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color string."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


def clamp(value, min_val=0, max_val=255):
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))


def apply_base_color(width, height, color_rgb):
    """Create base image with solid color fill."""
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    img_array[:, :] = color_rgb
    return img_array


def apply_simplex_noise(img_array, scale=0.01, intensity=15, seed=None):
    """Apply Perlin/Simplex noise for large-scale tonal variation."""
    height, width = img_array.shape[:2]
    
    if seed is None:
        seed = random.randint(0, 10000)
    
    noise_gen = OpenSimplex(seed=seed)
    
    for y in range(height):
        for x in range(width):
            noise_val = noise_gen.noise2(x * scale, y * scale)
            # Noise is between -1 and 1, scale to intensity
            adjustment = noise_val * intensity
            
            for c in range(3):
                img_array[y, x, c] = clamp(img_array[y, x, c] + adjustment)
    
    return img_array


def apply_fine_grain(img_array, intensity=8, seed=None):
    """Apply fine grain/sand texture with high-frequency noise."""
    height, width = img_array.shape[:2]
    
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random noise
    noise = np.random.randint(-intensity, intensity + 1, (height, width, 3), dtype=np.int16)
    
    # Add noise to image
    result = img_array.astype(np.int16) + noise
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return result


def apply_speckles(img_array, count=500, min_size=1, max_size=4, seed=None):
    """Apply speckles and aggregate spots of varying sizes."""
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)
    height, width = img_array.shape[:2]
    
    for _ in range(count):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(min_size, max_size)
        
        # Random color variation - darker or lighter
        if random.random() > 0.5:
            # Darker spot
            factor = random.uniform(0.6, 0.85)
        else:
            # Lighter spot
            factor = random.uniform(1.1, 1.3)
        
        base_color = img_array[y, x]
        spot_color = tuple(int(clamp(c * factor)) for c in base_color)
        
        # Draw irregular spot
        draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], 
                     fill=spot_color)
    
    return np.array(img)


def apply_cracks(img_array, count=20, seed=None):
    """Apply micro-cracks and hairline fractures."""
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)
    height, width = img_array.shape[:2]
    
    for _ in range(count):
        # Random starting point
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        
        # Random crack length and direction
        length = random.randint(10, 50)
        angle = random.uniform(0, 360)
        
        # Draw meandering crack
        points = [(x, y)]
        for i in range(length):
            angle += random.uniform(-30, 30)  # Meander
            x += np.cos(np.radians(angle)) * random.uniform(0.5, 2)
            y += np.sin(np.radians(angle)) * random.uniform(0.5, 2)
            
            if 0 <= x < width and 0 <= y < height:
                points.append((int(x), int(y)))
        
        if len(points) > 1:
            # Draw crack as dark line
            base_color = img_array[int(points[0][1]), int(points[0][0])]
            crack_color = tuple(int(c * 0.7) for c in base_color)
            draw.line(points, fill=crack_color, width=1)
    
    return np.array(img)


def apply_pores(img_array, count=300, size_range=(1, 2), seed=None):
    """Apply surface pores and pinholes."""
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)
    height, width = img_array.shape[:2]
    
    for _ in range(count):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(size_range[0], size_range[1])
        
        # Dark pore color
        base_color = img_array[y, x]
        pore_color = tuple(int(c * 0.5) for c in base_color)
        
        draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], 
                     fill=pore_color)
    
    return np.array(img)


def apply_color_variation(img_array, patch_count=10, scale=0.005, intensity=20, seed=None):
    """Apply subtle color variation and staining."""
    height, width = img_array.shape[:2]
    
    if seed is None:
        seed = random.randint(0, 10000)
    
    noise_gen = OpenSimplex(seed=seed)
    
    # Create variation mask
    for y in range(height):
        for x in range(width):
            # Use different frequency for variation
            noise_val = noise_gen.noise2(x * scale, y * scale)
            
            # Apply hue shift
            if noise_val > 0.3:  # Only in certain areas
                adjustment = noise_val * intensity
                for c in range(3):
                    img_array[y, x, c] = clamp(img_array[y, x, c] + adjustment)
    
    return img_array


def apply_dust_haze(img_array, patch_count=15, intensity=20, seed=None):
    """Apply dust and light surface haze."""
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    height, width = img_array.shape[:2]
    
    for _ in range(patch_count):
        # Random dust patch
        x = random.randint(-50, width)
        y = random.randint(-50, height)
        size = random.randint(50, 150)
        
        # Semi-transparent white
        alpha = random.randint(10, 30)
        draw.ellipse([x - size, y - size, x + size, y + size], 
                     fill=(255, 255, 255, alpha))
    
    # Blur the overlay
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=20))
    
    # Composite with original
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    
    return np.array(img)


def generate_concrete_texture(base_color, width=1024, height=1024, seed=None):
    """
    Generate a realistic concrete texture with all imperfections.
    
    Args:
        base_color: RGB tuple or hex color string
        width: Image width in pixels
        height: Image height in pixels
        seed: Random seed for reproducibility
    
    Returns:
        PIL Image object
    """
    if isinstance(base_color, str):
        base_color = hex_to_rgb(base_color)
    
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    print(f"Generating {width}x{height} concrete texture...")
    print(f"Base color: RGB{base_color} ({rgb_to_hex(base_color)})")
    
    # Step 1: Base color
    print("  - Applying base color...")
    img_array = apply_base_color(width, height, base_color)
    
    # Step 2: Simplex noise
    print("  - Adding Perlin/Simplex noise...")
    img_array = apply_simplex_noise(img_array, scale=0.01, intensity=15)
    
    # Step 3: Fine grain
    print("  - Adding fine grain texture...")
    img_array = apply_fine_grain(img_array, intensity=8)
    
    # Step 4: Speckles
    print("  - Adding speckles and aggregate...")
    img_array = apply_speckles(img_array, count=500, min_size=1, max_size=4)
    
    # Step 5: Color variation
    print("  - Adding color variation...")
    img_array = apply_color_variation(img_array, patch_count=10, scale=0.005, intensity=20)
    
    # Step 6: Cracks
    print("  - Adding micro-cracks...")
    img_array = apply_cracks(img_array, count=20)
    
    # Step 7: Pores
    print("  - Adding surface pores...")
    img_array = apply_pores(img_array, count=300, size_range=(1, 2))
    
    # Step 8: Dust haze
    print("  - Adding dust haze...")
    img_array = apply_dust_haze(img_array, patch_count=15, intensity=20)
    
    return Image.fromarray(img_array)


def show_palette():
    """Display the concrete color palette."""
    print("\n=== Concrete Color Palette ===\n")
    for num, info in sorted(CONCRETE_PALETTE.items()):
        print(f"{num:2d}. {info['name']:20s} - {info['color']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Generate realistic concrete textures with natural imperfections.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --color "#8C8680" --output my_concrete.png
  %(prog)s --palette
  %(prog)s --random --width 2048 --height 2048
  %(prog)s --preset 5 --output light_cement.png
        """
    )
    
    # Color selection options
    color_group = parser.add_mutually_exclusive_group()
    color_group.add_argument('--color', type=str, 
                            help='Hex color code (e.g., "#8C8680")')
    color_group.add_argument('--palette', action='store_true',
                            help='Show color palette and select by number')
    color_group.add_argument('--random', action='store_true',
                            help='Use random color from palette')
    color_group.add_argument('--preset', type=int,
                            help='Use preset color by number (1-12)')
    
    # Image dimensions
    parser.add_argument('--width', type=int, default=1024,
                       help='Image width in pixels (default: 1024)')
    parser.add_argument('--height', type=int, default=1024,
                       help='Image height in pixels (default: 1024)')
    
    # Output
    parser.add_argument('--output', type=str, default='concrete_texture.png',
                       help='Output file path (default: concrete_texture.png)')
    
    # Seed for reproducibility
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Handle palette display mode
    if args.palette:
        show_palette()
        try:
            choice = int(input("Select a color number (1-12): "))
            if choice not in CONCRETE_PALETTE:
                print(f"Invalid choice. Please select 1-{len(CONCRETE_PALETTE)}.")
                return 1
            base_color = CONCRETE_PALETTE[choice]['color']
            print(f"\nSelected: {CONCRETE_PALETTE[choice]['name']} ({base_color})\n")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return 0
    elif args.random:
        choice = random.choice(list(CONCRETE_PALETTE.keys()))
        base_color = CONCRETE_PALETTE[choice]['color']
        print(f"\nRandom selection: {CONCRETE_PALETTE[choice]['name']} ({base_color})\n")
    elif args.preset:
        if args.preset not in CONCRETE_PALETTE:
            print(f"Invalid preset. Please select 1-{len(CONCRETE_PALETTE)}.")
            return 1
        base_color = CONCRETE_PALETTE[args.preset]['color']
        print(f"\nUsing preset: {CONCRETE_PALETTE[args.preset]['name']} ({base_color})\n")
    elif args.color:
        base_color = args.color
    else:
        # Default to preset 6 (Classic Concrete)
        base_color = CONCRETE_PALETTE[6]['color']
        print(f"\nUsing default: {CONCRETE_PALETTE[6]['name']} ({base_color})\n")
    
    # Generate texture
    try:
        img = generate_concrete_texture(
            base_color=base_color,
            width=args.width,
            height=args.height,
            seed=args.seed
        )
        
        # Save image
        img.save(args.output)
        print(f"\n✓ Texture saved to: {args.output}")
        print(f"  Size: {args.width}x{args.height} pixels")
        print(f"  Base color: {base_color}")
        
        return 0
    except Exception as e:
        print(f"\n✗ Error generating texture: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
