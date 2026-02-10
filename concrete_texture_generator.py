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
from scipy.ndimage import gaussian_filter


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
    """Apply multi-octave Perlin/Simplex noise for large-scale tonal variation."""
    height, width = img_array.shape[:2]
    
    if seed is None:
        seed = random.randint(0, 10000)
    
    noise_gen = OpenSimplex(seed=seed)
    
    # Multi-octave noise for more natural variation
    # Octave 1: Large-scale variation
    for y in range(height):
        for x in range(width):
            noise_val = noise_gen.noise2(x * scale, y * scale)
            adjustment = noise_val * intensity
            
            for c in range(3):
                img_array[y, x, c] = clamp(img_array[y, x, c] + adjustment)
    
    # Octave 2: Medium-scale patches (higher frequency, lower intensity)
    noise_gen2 = OpenSimplex(seed=seed + 1)
    for y in range(height):
        for x in range(width):
            noise_val = noise_gen2.noise2(x * scale * 3, y * scale * 3)
            adjustment = noise_val * (intensity * 0.5)
            
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


def apply_knockdown_splatter(img_array, intensity=0.7, blur_radius=2, seed=None):
    """
    Apply knockdown splatter pattern - THE KEY LAYER for spray-on concrete.
    Creates the characteristic spray-and-flatten pattern with hills and valleys.
    """
    height, width = img_array.shape[:2]
    
    if seed is not None:
        np.random.seed(seed)
    
    # Generate high-frequency random noise
    splatter_noise = np.random.rand(height, width).astype(np.float32)
    
    # Threshold to create splatter droplets (only keep high values)
    threshold = 0.65  # Adjust to control splatter density
    splatter_mask = (splatter_noise > threshold).astype(np.float32)
    
    # Apply Gaussian blur to create the "knocked down" flattened mounds effect
    splatter_mask = gaussian_filter(splatter_mask, sigma=blur_radius)
    
    # Normalize and scale the splatter effect
    if splatter_mask.max() > 0:
        splatter_mask = splatter_mask / splatter_mask.max()
    
    # Apply splatter pattern to create hills (brighter) and valleys (darker)
    for c in range(3):
        # Create variation: some areas raised (lighter), some depressed (darker)
        variation = (splatter_mask - 0.5) * intensity * 40  # Scale for visibility
        img_array[:, :, c] = np.clip(img_array[:, :, c] + variation, 0, 255).astype(np.uint8)
    
    return img_array


def apply_heavy_stipple(img_array, intensity=15, seed=None):
    """
    Apply heavy stipple/grain - aggressive high-frequency per-pixel noise.
    NOT subtle - makes the surface look visibly gritty and sandy like concrete aggregate.
    """
    height, width = img_array.shape[:2]
    
    if seed is not None:
        np.random.seed(seed)
    
    # Generate aggressive random noise - much stronger than fine grain
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


def apply_cracks(img_array, density=1.0, seed=None):
    """Apply micro-cracks and hairline fractures - thin, jagged, meandering dark lines."""
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)
    height, width = img_array.shape[:2]
    
    # Calculate count based on density
    count = int(20 * density)
    
    for _ in range(count):
        # Random starting point
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        
        # Random crack length and direction
        length = random.randint(15, 60)  # Longer cracks
        angle = random.uniform(0, 360)
        
        # Draw meandering crack - more jagged
        points = [(x, y)]
        for i in range(length):
            # More aggressive angle changes for jagged appearance
            angle += random.uniform(-45, 45)  # Wider angle range
            step_size = random.uniform(0.3, 1.5)
            x += np.cos(np.radians(angle)) * step_size
            y += np.sin(np.radians(angle)) * step_size
            
            if 0 <= x < width and 0 <= y < height:
                points.append((int(x), int(y)))
        
        if len(points) > 1:
            # Draw crack as darker line
            base_color = img_array[int(points[0][1]), int(points[0][0])]
            crack_color = tuple(int(c * 0.6) for c in base_color)  # Darker
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


def apply_pitting_pinholes(img_array, density=1.0, seed=None):
    """
    Apply pitting/pinholes - small dark circular holes scattered across surface.
    These simulate trapped air bubbles and should be clearly visible as dark spots.
    """
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)
    height, width = img_array.shape[:2]
    
    # Calculate count based on density and image size
    base_count = int((width * height) / 1000 * density)
    
    for _ in range(base_count):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        # Varying sizes: 1-4px radius as specified
        radius = random.randint(1, 4)
        
        # Dark pinhole color - more prominent than before
        base_color = img_array[y, x]
        pinhole_color = tuple(int(c * 0.4) for c in base_color)  # Darker than before
        
        draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                     fill=pinhole_color)
    
    return np.array(img)


def apply_rough_aggregate(img_array, density=1.0, seed=None):
    """
    Apply rough aggregate / embedded stones - scattered spots with sharp contrast.
    These simulate visible sand grains and small stone chips (2-8px).
    """
    if seed is not None:
        random.seed(seed)
    
    img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(img)
    height, width = img_array.shape[:2]
    
    # Calculate count based on density and image size
    base_count = int((width * height) / 800 * density)
    
    for _ in range(base_count):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(2, 8)  # 2-8px as specified
        
        base_color = img_array[y, x]
        
        # Sharp contrast - both lighter and darker stones
        if random.random() > 0.5:
            # Darker stone/grain
            factor = random.uniform(0.5, 0.75)
        else:
            # Lighter stone/grain
            factor = random.uniform(1.25, 1.5)
        
        aggregate_color = tuple(int(clamp(c * factor)) for c in base_color)
        
        # Draw sharp-edged spot (no blur)
        draw.ellipse([x - size//2, y - size//2, x + size//2, y + size//2], 
                     fill=aggregate_color)
    
    return np.array(img)


def apply_color_variation(img_array, patch_count=10, scale=0.005, intensity=20, seed=None):
    """
    Apply surface staining - irregular darker patches with HARD edges (not soft blends).
    Simulates water marks and mineral deposits.
    """
    height, width = img_array.shape[:2]
    
    if seed is None:
        seed = random.randint(0, 10000)
    
    if seed is not None:
        np.random.seed(seed)
    
    noise_gen = OpenSimplex(seed=seed)
    
    # Create staining mask with hard edges using thresholding
    stain_mask = np.zeros((height, width), dtype=np.float32)
    
    for y in range(height):
        for x in range(width):
            # Use different frequency for variation
            noise_val = noise_gen.noise2(x * scale, y * scale)
            stain_mask[y, x] = noise_val
    
    # Apply threshold to create hard edges instead of smooth gradients
    threshold = 0.2
    stain_mask = (stain_mask > threshold).astype(np.float32)
    
    # Add some random irregular patches with hard edges
    for _ in range(patch_count):
        cx = random.randint(0, width - 1)
        cy = random.randint(0, height - 1)
        radius = random.randint(20, 80)
        
        # Create circular mask
        y_grid, x_grid = np.ogrid[:height, :width]
        dist_from_center = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
        circle_mask = (dist_from_center <= radius).astype(np.float32)
        
        # Add to stain mask
        stain_mask = np.maximum(stain_mask, circle_mask)
    
    # Apply staining (darker patches)
    for c in range(3):
        adjustment = stain_mask * (-intensity)  # Negative for darker stains
        img_array[:, :, c] = np.clip(img_array[:, :, c] + adjustment, 0, 255).astype(np.uint8)
    
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


def generate_concrete_texture(base_color, width=1024, height=1024, roughness=1.0, 
                            pitting=1.0, cracks=1.0, seed=None):
    """
    Generate a realistic spray-on concrete resurfacing texture with all imperfections.
    
    Args:
        base_color: RGB tuple or hex color string
        width: Image width in pixels
        height: Image height in pixels
        roughness: Overall grittiness/grain intensity (0.0-1.0, default 1.0)
        pitting: Density of pinholes (0.0-1.0, default 1.0)
        cracks: Micro-crack density (0.0-1.0, default 1.0)
        seed: Random seed for reproducibility
    
    Returns:
        PIL Image object
    """
    if isinstance(base_color, str):
        base_color = hex_to_rgb(base_color)
    
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    print(f"Generating {width}x{height} spray-on concrete texture...")
    print(f"Base color: RGB{base_color} ({rgb_to_hex(base_color)})")
    print(f"Parameters: roughness={roughness:.1f}, pitting={pitting:.1f}, cracks={cracks:.1f}")
    
    # Step 1: Base color
    print("  - Applying base color...")
    img_array = apply_base_color(width, height, base_color)
    
    # Step 2: Multi-octave Simplex noise (subtle undertone)
    print("  - Adding multi-octave Perlin/Simplex noise...")
    img_array = apply_simplex_noise(img_array, scale=0.01, intensity=12)
    
    # Step 3: KNOCKDOWN SPLATTER PATTERN - THE KEY LAYER
    print("  - Adding knockdown splatter pattern (KEY LAYER)...")
    img_array = apply_knockdown_splatter(img_array, intensity=0.8, blur_radius=2.5)
    
    # Step 4: Heavy stipple/grain - make it HARSH and GRITTY
    print("  - Adding heavy stipple/grain texture...")
    stipple_intensity = int(18 * roughness)  # Scale by roughness parameter
    img_array = apply_heavy_stipple(img_array, intensity=stipple_intensity)
    
    # Step 5: Fine grain (additional layer for more texture)
    print("  - Adding fine grain layer...")
    fine_intensity = int(10 * roughness)
    img_array = apply_fine_grain(img_array, intensity=fine_intensity)
    
    # Step 6: Pitting/pinholes - clearly visible dark spots
    print("  - Adding pitting/pinholes...")
    img_array = apply_pitting_pinholes(img_array, density=pitting)
    
    # Step 7: Rough aggregate/embedded stones
    print("  - Adding rough aggregate/embedded stones...")
    img_array = apply_rough_aggregate(img_array, density=roughness)
    
    # Step 8: Surface staining with HARD edges
    print("  - Adding surface staining (hard edges)...")
    img_array = apply_color_variation(img_array, patch_count=8, scale=0.008, intensity=15)
    
    # Step 9: Micro-cracks - jagged and meandering
    print("  - Adding micro-cracks...")
    img_array = apply_cracks(img_array, density=cracks)
    
    # Step 10: Legacy pores (keeping for backwards compatibility)
    print("  - Adding additional surface pores...")
    pore_count = int(200 * pitting)
    img_array = apply_pores(img_array, count=pore_count, size_range=(1, 2))
    
    # Step 11: Dust haze (subtle)
    print("  - Adding dust/efflorescence (subtle)...")
    img_array = apply_dust_haze(img_array, patch_count=12, intensity=15)
    
    return Image.fromarray(img_array)


def show_palette():
    """Display the concrete color palette."""
    print("\n=== Concrete Color Palette ===\n")
    for num, info in sorted(CONCRETE_PALETTE.items()):
        print(f"{num:2d}. {info['name']:20s} - {info['color']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Generate realistic spray-on concrete resurfacing textures with natural imperfections.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --color "#8C8680" --output my_concrete.png
  %(prog)s --palette
  %(prog)s --random --width 2048 --height 2048
  %(prog)s --preset 5 --output light_cement.png
  %(prog)s --color "#8C8680" --roughness 0.8 --pitting 1.2 --cracks 0.5
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
    
    # Texture parameters
    parser.add_argument('--roughness', type=float, default=1.0,
                       help='Overall grittiness/grain intensity (0.0-1.0, default: 1.0)')
    parser.add_argument('--pitting', type=float, default=1.0,
                       help='Density of pinholes (0.0-1.0, default: 1.0)')
    parser.add_argument('--cracks', type=float, default=1.0,
                       help='Micro-crack density (0.0-1.0, default: 1.0)')
    
    # Output
    parser.add_argument('--output', type=str, default='concrete_texture.png',
                       help='Output file path (default: concrete_texture.png)')
    
    # Seed for reproducibility
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Validate texture parameters
    if not (0.0 <= args.roughness <= 2.0):
        print("Warning: roughness should be between 0.0 and 2.0, clamping...")
        args.roughness = max(0.0, min(2.0, args.roughness))
    
    if not (0.0 <= args.pitting <= 2.0):
        print("Warning: pitting should be between 0.0 and 2.0, clamping...")
        args.pitting = max(0.0, min(2.0, args.pitting))
    
    if not (0.0 <= args.cracks <= 2.0):
        print("Warning: cracks should be between 0.0 and 2.0, clamping...")
        args.cracks = max(0.0, min(2.0, args.cracks))
    
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
            roughness=args.roughness,
            pitting=args.pitting,
            cracks=args.cracks,
            seed=args.seed
        )
        
        # Save image
        img.save(args.output)
        print(f"\n✓ Texture saved to: {args.output}")
        print(f"  Size: {args.width}x{args.height} pixels")
        print(f"  Base color: {base_color}")
        print(f"  Roughness: {args.roughness:.1f}, Pitting: {args.pitting:.1f}, Cracks: {args.cracks:.1f}")
        
        return 0
    except Exception as e:
        print(f"\n✗ Error generating texture: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
