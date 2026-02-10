#!/usr/bin/env python3
"""
Concrete Texture Generator

A procedural texture generator that creates realistic concrete textures
with various imperfections like noise, grain, speckles, cracks, pores, and stains.
"""

import argparse
import random
import sys
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from opensimplex import OpenSimplex


# Preset concrete color palette inspired by reference images
CONCRETE_PALETTE = {
    1: {"name": "Light Grey", "hex": "#C8C4BC", "rgb": (200, 196, 188)},
    2: {"name": "Warm Grey", "hex": "#B5A898", "rgb": (181, 168, 152)},
    3: {"name": "Cool Grey", "hex": "#A8ACB0", "rgb": (168, 172, 176)},
    4: {"name": "Beige Concrete", "hex": "#D4CFC5", "rgb": (212, 207, 197)},
    5: {"name": "Medium Grey", "hex": "#8C8680", "rgb": (140, 134, 128)},
    6: {"name": "Dark Charcoal", "hex": "#5A5A5A", "rgb": (90, 90, 90)},
    7: {"name": "Cement Grey", "hex": "#9B9B9B", "rgb": (155, 155, 155)},
    8: {"name": "Stone Grey", "hex": "#7D7D7D", "rgb": (125, 125, 125)},
    9: {"name": "Warm Beige", "hex": "#BFB5A8", "rgb": (191, 181, 168)},
    10: {"name": "Dark Grey", "hex": "#6B6B6B", "rgb": (107, 107, 107)},
    11: {"name": "Light Cement", "hex": "#DCDCDC", "rgb": (220, 220, 220)},
    12: {"name": "Graphite", "hex": "#4A4A4A", "rgb": (74, 74, 74)},
}


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color format: must be 6 characters after '#'")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def apply_base_color(width: int, height: int, color: Tuple[int, int, int]) -> np.ndarray:
    """
    Create base color fill for the texture.
    
    Args:
        width: Image width
        height: Image height
        color: RGB color tuple
    
    Returns:
        numpy array with base color
    """
    base = np.zeros((height, width, 3), dtype=np.float64)
    base[:, :] = color
    return base


def apply_perlin_noise(width: int, height: int, scale: float = 100.0, 
                       intensity: float = 15.0) -> np.ndarray:
    """
    Generate Perlin/Simplex noise layer for large-scale tonal variation.
    
    Args:
        width: Image width
        height: Image height
        scale: Scale of the noise pattern (higher = larger features)
        intensity: Strength of the noise effect
    
    Returns:
        numpy array with noise values
    """
    noise_gen = OpenSimplex(seed=random.randint(0, 1000000))
    
    # Create coordinate grids for vectorized operation
    x_coords = np.arange(width) / scale
    y_coords = np.arange(height) / scale
    
    # Generate noise using list comprehension (more efficient than nested loops)
    noise = np.array([[noise_gen.noise2(x, y) for x in x_coords] for y in y_coords])
    
    # Normalize to -intensity to +intensity range
    noise = noise * intensity
    return noise


def apply_fine_grain(width: int, height: int, intensity: float = 8.0) -> np.ndarray:
    """
    Generate fine grain/sand texture with high-frequency per-pixel noise.
    
    Args:
        width: Image width
        height: Image height
        intensity: Strength of the grain effect
    
    Returns:
        numpy array with grain noise
    """
    grain = np.random.normal(0, intensity, (height, width))
    return grain


def apply_speckles(img_array: np.ndarray, num_speckles: int = 500,
                   size_range: Tuple[int, int] = (1, 4)) -> np.ndarray:
    """
    Add random darker and lighter spots to simulate aggregate and small stones.
    
    Args:
        img_array: Base image array
        num_speckles: Number of speckles to add
        size_range: Min and max size of speckles
    
    Returns:
        Modified image array
    """
    height, width = img_array.shape[:2]
    result = img_array.copy()
    
    for _ in range(num_speckles):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(size_range[0], size_range[1])
        intensity = random.uniform(-30, 20)  # More dark than light
        
        # Create circular speckle
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if dx*dx + dy*dy <= size*size:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        result[ny, nx] += intensity
    
    return result


def apply_cracks(width: int, height: int, num_cracks: int = 8,
                 thickness: int = 1) -> Image.Image:
    """
    Generate micro-cracks and hairline fractures.
    
    Args:
        width: Image width
        height: Image height
        num_cracks: Number of cracks to generate
        thickness: Line thickness of cracks
    
    Returns:
        PIL Image with crack overlay
    """
    crack_layer = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(crack_layer)
    
    for _ in range(num_cracks):
        # Random starting point
        x = random.randint(0, width)
        y = random.randint(0, height)
        
        # Generate meandering crack
        points = [(x, y)]
        length = random.randint(50, 200)
        angle = random.uniform(0, 2 * np.pi)
        
        for step in range(length):
            # Add some randomness to create meandering effect
            angle += random.uniform(-0.3, 0.3)
            step_size = random.uniform(1, 3)
            
            x += np.cos(angle) * step_size
            y += np.sin(angle) * step_size
            
            # Keep within bounds
            x = max(0, min(width, x))
            y = max(0, min(height, y))
            
            points.append((int(x), int(y)))
        
        # Draw crack line
        if len(points) > 1:
            draw.line(points, fill=255, width=thickness)
    
    return crack_layer


def apply_pores(width: int, height: int, num_pores: int = 300) -> Image.Image:
    """
    Generate surface pores and pinholes (small dark dots).
    
    Args:
        width: Image width
        height: Image height
        num_pores: Number of pores to add
    
    Returns:
        PIL Image with pore overlay
    """
    pore_layer = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(pore_layer)
    
    for _ in range(num_pores):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        size = random.randint(1, 3)
        
        # Draw small dark circle
        draw.ellipse([x - size, y - size, x + size, y + size], fill=255)
    
    return pore_layer


def apply_color_variation(img_array: np.ndarray, num_patches: int = 20,
                         patch_size: int = 150, intensity: float = 10.0) -> np.ndarray:
    """
    Add subtle color variation patches to simulate stains and mineral deposits.
    
    Args:
        img_array: Base image array
        num_patches: Number of variation patches
        patch_size: Size of each patch
        intensity: Strength of color variation
    
    Returns:
        Modified image array
    """
    height, width = img_array.shape[:2]
    result = img_array.copy()
    
    for _ in range(num_patches):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        
        # Random hue shift
        hue_shift = np.array([
            random.uniform(-intensity, intensity),
            random.uniform(-intensity, intensity),
            random.uniform(-intensity, intensity)
        ])
        
        # Create circular gradient patch
        for y in range(max(0, cy - patch_size), min(height, cy + patch_size)):
            for x in range(max(0, cx - patch_size), min(width, cx + patch_size)):
                dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                if dist < patch_size:
                    # Gaussian falloff
                    falloff = np.exp(-(dist**2) / (2 * (patch_size / 2)**2))
                    result[y, x] += hue_shift * falloff
    
    return result


def apply_dust_haze(width: int, height: int, num_patches: int = 15,
                    patch_size: int = 200) -> Image.Image:
    """
    Generate faint lighter overlay patches for dust/surface haze effect.
    
    Args:
        width: Image width
        height: Image height
        num_patches: Number of dust patches
        patch_size: Size of each patch
    
    Returns:
        PIL Image with dust overlay
    """
    dust_layer = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(dust_layer)
    
    for _ in range(num_patches):
        cx = random.randint(-patch_size, width + patch_size)
        cy = random.randint(-patch_size, height + patch_size)
        
        # Draw semi-transparent ellipse
        intensity = random.randint(10, 30)
        draw.ellipse([cx - patch_size, cy - patch_size, 
                     cx + patch_size, cy + patch_size], fill=intensity)
    
    # Blur for smooth effect
    dust_layer = dust_layer.filter(ImageFilter.GaussianBlur(radius=patch_size // 4))
    
    return dust_layer


def generate_concrete_texture(width: int, height: int, 
                              base_color: Tuple[int, int, int],
                              output_path: str) -> None:
    """
    Generate a complete realistic concrete texture with all layers.
    
    Args:
        width: Image width in pixels
        height: Image height in pixels
        base_color: RGB tuple for base concrete color
        output_path: Path to save the generated image
    """
    print(f"Generating concrete texture...")
    print(f"  Size: {width}x{height}")
    print(f"  Base color: RGB{base_color}")
    
    # Start with base color
    texture = apply_base_color(width, height, base_color)
    
    # Apply Perlin noise for large-scale variation
    print("  Applying Perlin noise...")
    perlin = apply_perlin_noise(width, height, scale=100.0, intensity=15.0)
    texture[:, :, 0] += perlin
    texture[:, :, 1] += perlin
    texture[:, :, 2] += perlin
    
    # Apply fine grain texture
    print("  Applying fine grain...")
    grain = apply_fine_grain(width, height, intensity=8.0)
    texture[:, :, 0] += grain
    texture[:, :, 1] += grain
    texture[:, :, 2] += grain
    
    # Apply color variation patches
    print("  Applying color variation...")
    texture = apply_color_variation(texture, num_patches=20, patch_size=150, intensity=10.0)
    
    # Apply speckles and aggregate
    print("  Applying speckles...")
    texture = apply_speckles(texture, num_speckles=500, size_range=(1, 4))
    
    # Clip values to valid range
    texture = np.clip(texture, 0, 255)
    
    # Convert to PIL Image
    img = Image.fromarray(texture.astype(np.uint8), mode='RGB')
    
    # Generate and apply cracks
    print("  Applying micro-cracks...")
    crack_layer = apply_cracks(width, height, num_cracks=8, thickness=1)
    crack_array = np.array(crack_layer, dtype=np.float64) / 255.0
    img_array = np.array(img, dtype=np.float64)
    img_array -= crack_array[:, :, np.newaxis] * 25  # Darken cracks
    img_array = np.clip(img_array, 0, 255)
    img = Image.fromarray(img_array.astype(np.uint8), mode='RGB')
    
    # Generate and apply pores
    print("  Applying surface pores...")
    pore_layer = apply_pores(width, height, num_pores=300)
    pore_array = np.array(pore_layer, dtype=np.float64) / 255.0
    img_array = np.array(img, dtype=np.float64)
    img_array -= pore_array[:, :, np.newaxis] * 40  # Darken pores
    img_array = np.clip(img_array, 0, 255)
    img = Image.fromarray(img_array.astype(np.uint8), mode='RGB')
    
    # Generate and apply dust haze
    print("  Applying dust haze...")
    dust_layer = apply_dust_haze(width, height, num_patches=15, patch_size=200)
    dust_array = np.array(dust_layer, dtype=np.float64) / 255.0
    img_array = np.array(img, dtype=np.float64)
    img_array += dust_array[:, :, np.newaxis] * 15  # Lighten dust areas
    img_array = np.clip(img_array, 0, 255)
    img = Image.fromarray(img_array.astype(np.uint8), mode='RGB')
    
    # Save the image
    img.save(output_path)
    print(f"\n✓ Texture saved to: {output_path}")
    print(f"  Base color used: RGB{base_color}")
    print(f"  Image size: {width}x{height} pixels")


def show_palette():
    """Display the concrete color palette for user selection."""
    print("\n" + "="*60)
    print("CONCRETE COLOR PALETTE")
    print("="*60)
    
    for num, color_info in CONCRETE_PALETTE.items():
        name = color_info["name"]
        hex_code = color_info["hex"]
        rgb = color_info["rgb"]
        print(f"  {num:2d}. {name:20s} {hex_code}  RGB{rgb}")
    
    print("="*60)
    
    while True:
        try:
            choice = input("\nEnter color number (1-12) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= 12:
                return CONCRETE_PALETTE[choice_num]["rgb"]
            else:
                print("Invalid choice. Please enter a number between 1 and 12.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_random_color() -> Tuple[int, int, int]:
    """Get a random concrete color from the palette."""
    choice = random.choice(list(CONCRETE_PALETTE.values()))
    print(f"Random color selected: {choice['name']} {choice['hex']}")
    return choice["rgb"]


def main():
    """Main entry point for the concrete texture generator."""
    parser = argparse.ArgumentParser(
        description="Generate realistic concrete texture images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate with specific hex color
  python concrete_texture_generator.py --color "#8C8680" --width 1024 --height 1024 --output my_concrete.png
  
  # Show color palette and pick
  python concrete_texture_generator.py --palette
  
  # Use random concrete color
  python concrete_texture_generator.py --random
        """
    )
    
    parser.add_argument('--color', type=str, help='Hex color code (e.g., "#8C8680")')
    parser.add_argument('--palette', action='store_true', 
                       help='Show color palette and select interactively')
    parser.add_argument('--random', action='store_true',
                       help='Use random concrete color from palette')
    parser.add_argument('--width', type=int, default=1024,
                       help='Image width in pixels (default: 1024)')
    parser.add_argument('--height', type=int, default=1024,
                       help='Image height in pixels (default: 1024)')
    parser.add_argument('--output', type=str, default='concrete_texture.png',
                       help='Output file path (default: concrete_texture.png)')
    
    args = parser.parse_args()
    
    # Determine base color
    base_color = None
    
    if args.palette:
        base_color = show_palette()
    elif args.random:
        base_color = get_random_color()
    elif args.color:
        try:
            base_color = hex_to_rgb(args.color)
        except (ValueError, IndexError):
            print(f"Error: Invalid hex color '{args.color}'")
            print("Please use format: #RRGGBB (e.g., #8C8680)")
            sys.exit(1)
    else:
        # Default: show palette
        base_color = show_palette()
    
    # Generate texture
    generate_concrete_texture(args.width, args.height, base_color, args.output)


if __name__ == '__main__':
    main()
