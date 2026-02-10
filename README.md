# Concrete Texture Creator

A Python application that **procedurally generates realistic-looking concrete texture images** with various visual imperfections that real concrete has.

## Features

This texture generator creates high-quality, realistic concrete textures with the following visual characteristics:

1. ✅ **Base color fill** — User-supplied color (hex string or RGB tuple)
2. ✅ **Perlin / Simplex noise layer** — Subtle, large-scale tonal variation
3. ✅ **Fine grain / sand texture** — High-frequency per-pixel noise
4. ✅ **Speckles & aggregate spots** — Random darker/lighter spots of varying sizes
5. ✅ **Micro-cracks / hairline fractures** — Thin, semi-random meandering lines
6. ✅ **Surface pores / pinholes** — Small dark dots simulating air bubbles
7. ✅ **Subtle color variation / staining** — Shifted hue/saturation patches
8. ✅ **Dust / light surface haze** — Faint lighter overlay in random patches

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- **Pillow** (PIL) — Image processing
- **NumPy** — Numerical operations
- **opensimplex** — Perlin/Simplex noise generation

## Usage

### Option 1: Specify a Hex Color

Generate a concrete texture with a specific color:

```bash
python concrete_texture_generator.py --color "#8C8680" --width 1024 --height 1024 --output my_concrete.png
```

### Option 2: Choose from Color Palette

Show a palette of preset concrete colors and pick one interactively:

```bash
python concrete_texture_generator.py --palette
```

The palette includes 12 realistic concrete colors:
1. Light Grey (#C8C4BC)
2. Warm Grey (#B5A898)
3. Cool Grey (#A8ACB0)
4. Beige Concrete (#D4CFC5)
5. Medium Grey (#8C8680)
6. Dark Charcoal (#5A5A5A)
7. Cement Grey (#9B9B9B)
8. Stone Grey (#7D7D7D)
9. Warm Beige (#BFB5A8)
10. Dark Grey (#6B6B6B)
11. Light Cement (#DCDCDC)
12. Graphite (#4A4A4A)

### Option 3: Random Concrete Color

Generate a texture with a randomly selected color from the palette:

```bash
python concrete_texture_generator.py --random
```

### Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--color` | Hex color code (e.g., "#8C8680") | None |
| `--palette` | Show color palette and select interactively | False |
| `--random` | Use random concrete color from palette | False |
| `--width` | Image width in pixels | 1024 |
| `--height` | Image height in pixels | 1024 |
| `--output` | Output file path | concrete_texture.png |

## Examples

### Example 1: Medium Grey Concrete (1024x1024)

```bash
python concrete_texture_generator.py --color "#8C8680"
```

### Example 2: Large Dark Charcoal Texture (2048x2048)

```bash
python concrete_texture_generator.py --color "#5A5A5A" --width 2048 --height 2048 --output dark_concrete.png
```

### Example 3: Custom Size with Palette Selection

```bash
python concrete_texture_generator.py --palette --width 1920 --height 1080 --output wallpaper.png
```

### Example 4: Quick Random Generation

```bash
python concrete_texture_generator.py --random --output random_concrete.png
```

## Reference Images

This project includes two reference images of real concrete texture color samples:
- `Picture1.png` — Dark grey concrete color swatch
- `Picture2.jpg` — Dark grey concrete color swatch

These images inspired the color palette and texture characteristics.

## Output Information

When generating a texture, the tool displays:
- Generation progress (each layer being applied)
- Final texture size (width × height)
- Base color used (RGB values)
- Output file path

Example output:
```
Generating concrete texture...
  Size: 1024x1024
  Base color: RGB(140, 134, 128)
  Applying Perlin noise...
  Applying fine grain...
  Applying color variation...
  Applying speckles...
  Applying micro-cracks...
  Applying surface pores...
  Applying dust haze...

✓ Texture saved to: concrete_texture.png
  Base color used: RGB(140, 134, 128)
  Image size: 1024x1024 pixels
```

## Technical Details

### Texture Layers

Each visual element is implemented as a separate function for clarity and customization:

- **`apply_base_color()`** — Fills the canvas with the base color
- **`apply_perlin_noise()`** — Adds large-scale tonal variation using Simplex noise
- **`apply_fine_grain()`** — Adds high-frequency per-pixel noise for sandy texture
- **`apply_speckles()`** — Creates random aggregate spots and small stones
- **`apply_cracks()`** — Generates meandering hairline fractures
- **`apply_pores()`** — Adds small dark dots simulating air bubbles
- **`apply_color_variation()`** — Creates subtle stain-like patches
- **`apply_dust_haze()`** — Adds lighter patches for dust effect

### Customization

You can modify the intensity and density of each effect by editing the function calls in `generate_concrete_texture()`. Key parameters include:

- **Perlin noise**: `scale` (default: 100.0), `intensity` (default: 15.0)
- **Fine grain**: `intensity` (default: 8.0)
- **Speckles**: `num_speckles` (default: 500), `size_range` (default: 1-4)
- **Cracks**: `num_cracks` (default: 8), `thickness` (default: 1)
- **Pores**: `num_pores` (default: 300)
- **Color variation**: `num_patches` (default: 20), `patch_size` (default: 150)
- **Dust haze**: `num_patches` (default: 15), `patch_size` (default: 200)

## Code Structure

The script is well-organized with:
- Clear function separation for each texture layer
- Comprehensive docstrings
- Type hints for better code clarity
- Sensible default parameters
- Command-line interface with argparse

## License

This project is provided as-is for generating concrete textures.

## Contributing

Feel free to modify the texture parameters or add new concrete color presets to the `CONCRETE_PALETTE` dictionary.

## Troubleshooting

### ImportError: No module named 'opensimplex'

Make sure you've installed the dependencies:
```bash
pip install -r requirements.txt
```

### Memory issues with large textures

For very large textures (>4096x4096), consider reducing the number of texture elements or processing in smaller chunks.

## Future Enhancements

Potential improvements:
- Adjustable texture intensity parameters via CLI
- Different concrete finishes (polished, rough, weathered)
- Tileable texture generation
- Batch generation mode
- JSON configuration file support
