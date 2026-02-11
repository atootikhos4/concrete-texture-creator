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


# Concrete color presets - exact colors from requirements
CONCRETE_PALETTE = {
    1: {'name': 'Light Grey', 'color': '#C8C4BC'},
    2: {'name': 'Warm Grey', 'color': '#B5A898'},
    3: {'name': 'Cool Grey', 'color': '#A8ACB0'},
    4: {'name': 'Beige', 'color': '#D4CFC5'},
    5: {'name': 'Medium Grey', 'color': '#8C8680'},
    6: {'name': 'Dark Charcoal', 'color': '#5A5A5A'},
    7: {'name': 'Cement Grey', 'color': '#9B9B9B'},
    8: {'name': 'Stone Grey', 'color': '#7D7D7D'},
    9: {'name': 'Warm Beige', 'color': '#BFB5A8'},
    10: {'name': 'Dark Grey', 'color': '#6B6B6B'},
    11: {'name': 'Light Cement', 'color': '#DCDCDC'},
    12: {'name': 'Graphite', 'color': '#4A4A4A'},
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


def apply_fine_grain(img_array, intensity=35, seed=None):
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


def apply_knockdown_splatter(img_array, intensity=0.9, blur_radius=3, seed=None):
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
    threshold = 0.60  # Lower threshold = more splatter coverage (changed from 0.65)
    splatter_mask = (splatter_noise > threshold).astype(np.float32)
    
    # Apply Gaussian blur to create the "knocked down" flattened mounds effect
    splatter_mask = gaussian_filter(splatter_mask, sigma=blur_radius)
    
    # Normalize and scale the splatter effect
    if splatter_mask.max() > 0:
        splatter_mask = splatter_mask / splatter_mask.max()
    
    # Apply splatter pattern to create hills (brighter) and valleys (darker)
    for c in range(3):
        # Create variation: some areas raised (lighter), some depressed (darker)
        variation = (splatter_mask - 0.5) * intensity * 50  # Increased from 40 to 50 for MORE prominence
        img_array[:, :, c] = np.clip(img_array[:, :, c] + variation, 0, 255).astype(np.uint8)
    
    return img_array


def apply_heavy_stipple(img_array, intensity=40, seed=None):
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


def apply_speckles(img_array, count=1200, min_size=1, max_size=4, seed=None):
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
        
        # Draw meandering crack - MUCH more jagged
        points = [(x, y)]
        for i in range(length):
            # LARGE angular variation for very jagged appearance (±0.5-0.8 radians = ±29-46 degrees)
            # Let's use ±60-90 degrees for even MORE jagged cracks
            angle += random.uniform(-80, 80)  # Much wider angle range
            step_size = random.uniform(0.5, 2.0)  # More variable step sizes
            x += np.cos(np.radians(angle)) * step_size
            y += np.sin(np.radians(angle)) * step_size
            
            if 0 <= x < width and 0 <= y < height:
                points.append((int(x), int(y)))
            
            # Occasionally branch into sub-cracks
            if i > 5 and random.random() < 0.1:  # 10% chance to branch
                # Create short sub-crack
                branch_length = random.randint(3, 10)
                branch_angle = angle + random.uniform(-90, 90)
                branch_x, branch_y = x, y
                # Clamp starting position to valid bounds
                branch_x = max(0, min(width - 1, branch_x))
                branch_y = max(0, min(height - 1, branch_y))
                branch_points = [(int(branch_x), int(branch_y))]
                
                for _ in range(branch_length):
                    branch_angle += random.uniform(-60, 60)
                    branch_x += np.cos(np.radians(branch_angle)) * random.uniform(0.5, 1.5)
                    branch_y += np.sin(np.radians(branch_angle)) * random.uniform(0.5, 1.5)
                    
                    if 0 <= branch_x < width and 0 <= branch_y < height:
                        branch_points.append((int(branch_x), int(branch_y)))
                
                if len(branch_points) > 1:
                    base_color_branch = img_array[int(branch_points[0][1]), int(branch_points[0][0])]
                    crack_color_branch = tuple(int(c * 0.6) for c in base_color_branch)
                    draw.line(branch_points, fill=crack_color_branch, width=1)
        
        if len(points) > 1:
            # Draw crack as darker line
            base_color = img_array[int(points[0][1]), int(points[0][0])]
            crack_color = tuple(int(c * 0.6) for c in base_color)  # Darker
            draw.line(points, fill=crack_color, width=1)
    
    return np.array(img)


def apply_pores(img_array, count=800, size_range=(1, 3), seed=None):
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
        
        # Dark pore color - more prominent
        base_color = img_array[y, x]
        pore_color = tuple(int(c * 0.4) for c in base_color)  # Darker for visibility
        
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
    
    # Calculate count based on density and image size - increased significantly
    base_count = int((width * height) / 600 * density)  # Changed from 1000 to 600 for more pinholes
    
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
                            pitting=1.0, cracks=1.0, seed=None,
                            knockdown_intensity=0.9, knockdown_scale=3.0,
                            pitting_size=1.0, aggregate_density=1.0,
                            staining_intensity=1.0, noise_scale=1.0, verbose=True):
    """
    Generate a realistic spray-on concrete resurfacing texture with all imperfections.
    
    Args:
        base_color: RGB tuple or hex color string
        width: Image width in pixels
        height: Image height in pixels
        roughness: Overall grittiness/grain intensity (0.0-2.0, default 1.0)
        pitting: Density of pinholes (0.0-2.0, default 1.0)
        cracks: Micro-crack density (0.0-2.0, default 1.0)
        seed: Random seed for reproducibility
        knockdown_intensity: Knockdown splatter intensity (0.0-1.0, default 0.9)
        knockdown_scale: Knockdown splatter scale/blur (1.0-5.0, default 3.0)
        pitting_size: Size multiplier for pitting (0.5-2.0, default 1.0)
        aggregate_density: Density of aggregate particles (0.0-2.0, default 1.0)
        staining_intensity: Intensity of surface staining (0.0-2.0, default 1.0)
        noise_scale: Scale of Perlin noise (0.5-2.0, default 1.0)
        verbose: Print progress messages (default True)
    
    Returns:
        PIL Image object
    """
    if isinstance(base_color, str):
        base_color = hex_to_rgb(base_color)
    
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    if verbose:
        print(f"Generating {width}x{height} spray-on concrete texture...")
        print(f"Base color: RGB{base_color} ({rgb_to_hex(base_color)})")
        print(f"Parameters: roughness={roughness:.1f}, pitting={pitting:.1f}, cracks={cracks:.1f}")
    
    # Step 1: Base color
    if verbose:
        print("  - Applying base color...")
    img_array = apply_base_color(width, height, base_color)
    
    # Step 2: Multi-octave Simplex noise (subtle undertone)
    if verbose:
        print("  - Adding multi-octave Perlin/Simplex noise...")
    noise_scale_val = 0.01 * noise_scale
    img_array = apply_simplex_noise(img_array, scale=noise_scale_val, intensity=12)
    
    # Step 3: KNOCKDOWN SPLATTER PATTERN - THE KEY LAYER
    if verbose:
        print("  - Adding knockdown splatter pattern (KEY LAYER)...")
    img_array = apply_knockdown_splatter(img_array, intensity=knockdown_intensity, blur_radius=knockdown_scale)
    
    # Step 4: Heavy stipple/grain - make it HARSH and GRITTY
    if verbose:
        print("  - Adding heavy stipple/grain texture...")
    stipple_intensity = int(35 * roughness)  # Scale by roughness parameter - much more aggressive
    img_array = apply_heavy_stipple(img_array, intensity=stipple_intensity)
    
    # Step 5: Fine grain (additional layer for more texture)
    if verbose:
        print("  - Adding fine grain layer...")
    fine_intensity = int(25 * roughness)  # Increased from 10 to 25
    img_array = apply_fine_grain(img_array, intensity=fine_intensity)
    
    # Step 6: Pitting/pinholes - clearly visible dark spots
    if verbose:
        print("  - Adding pitting/pinholes...")
    img_array = apply_pitting_pinholes(img_array, density=pitting)
    
    # Step 7: Rough aggregate/embedded stones
    if verbose:
        print("  - Adding rough aggregate/embedded stones...")
    img_array = apply_rough_aggregate(img_array, density=aggregate_density)
    
    # Step 8: Surface staining with HARD edges
    if verbose:
        print("  - Adding surface staining (hard edges)...")
    stain_intensity = int(15 * staining_intensity)
    img_array = apply_color_variation(img_array, patch_count=8, scale=0.008, intensity=stain_intensity)
    
    # Step 9: Micro-cracks - jagged and meandering
    if verbose:
        print("  - Adding micro-cracks...")
    img_array = apply_cracks(img_array, density=cracks)
    
    # Step 10: Legacy pores (keeping for backwards compatibility)
    if verbose:
        print("  - Adding additional surface pores...")
    pore_count = int(600 * pitting)  # Increased from 200
    pore_size = (int(1 * pitting_size), int(3 * pitting_size))  # Increased max from 2 to 3
    img_array = apply_pores(img_array, count=pore_count, size_range=pore_size)
    
    # Step 11: Dust haze (subtle)
    if verbose:
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
                       help='Overall grittiness/grain intensity (0.0-2.0, default: 1.0)')
    parser.add_argument('--splatter', type=float, default=0.9,
                       help='Knockdown splatter intensity (0.0-1.0, default: 0.9)')
    parser.add_argument('--pitting', type=float, default=1.0,
                       help='Density of pinholes (0.0-2.0, default: 1.0)')
    parser.add_argument('--cracks', type=float, default=1.0,
                       help='Micro-crack density (0.0-2.0, default: 1.0)')
    
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
    
    if not (0.0 <= args.splatter <= 1.0):
        print("Warning: splatter should be between 0.0 and 1.0, clamping...")
        args.splatter = max(0.0, min(1.0, args.splatter))
    
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
        # Default to preset 5 (Medium Grey)
        base_color = CONCRETE_PALETTE[5]['color']
        print(f"\nUsing default: {CONCRETE_PALETTE[5]['name']} ({base_color})\n")
    
    # Generate texture
    try:
        img = generate_concrete_texture(
            base_color=base_color,
            width=args.width,
            height=args.height,
            roughness=args.roughness,
            pitting=args.pitting,
            cracks=args.cracks,
            knockdown_intensity=args.splatter,
            seed=args.seed
        )
        
        # Save image
        img.save(args.output)
        print(f"\n✓ Texture saved to: {args.output}")
        print(f"  Size: {args.width}x{args.height} pixels")
        print(f"  Base color: {base_color}")
        print(f"  Roughness: {args.roughness:.1f}, Splatter: {args.splatter:.1f}, Pitting: {args.pitting:.1f}, Cracks: {args.cracks:.1f}")
        
        return 0
    except Exception as e:
        print(f"\n✗ Error generating texture: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
