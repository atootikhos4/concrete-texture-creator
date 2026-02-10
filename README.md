# Concrete Texture Generator

A Python-based procedural texture generator that creates realistic concrete textures with natural imperfections. The color palette is inspired by real concrete samples from the reference images included in this repository.

## Features

This generator creates highly realistic concrete textures by layering multiple effects:

1. **Base Color Fill** — Customizable base concrete color
2. **Perlin/Simplex Noise** — Large-scale tonal variation for natural unevenness
3. **Fine Grain/Sand Texture** — High-frequency noise mimicking sandy surface
4. **Speckles & Aggregate Spots** — Random spots of varying sizes simulating stones and aggregate
5. **Micro-cracks/Hairline Fractures** — Thin, meandering lines across the surface
6. **Surface Pores/Pinholes** — Small dark dots simulating trapped air bubbles
7. **Color Variation/Staining** — Subtle patches simulating water stains or mineral deposits
8. **Dust/Light Surface Haze** — Faint lighter overlay in random patches

## Reference Images

The color palette was extracted from real concrete samples:
- `Picture1.png` — Concrete color swatch/sample image
- `Picture2.jpg` — Concrete color swatch/sample image
- `ye.pptx` — PowerPoint with concrete texture color samples on the first slide

## Installation

### Requirements
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/atootikhos4/concrete-texture-creator.git
cd concrete-texture-creator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The generator provides three ways to specify the concrete color:

### 1. Hex Color Input

Specify a custom hex color:

```bash
python concrete_texture_generator.py --color "#8C8680" --output my_concrete.png
```

### 2. Palette Mode

Display the preset color palette and select by number:

```bash
python concrete_texture_generator.py --palette
```

This will show all available presets:
```
=== Concrete Color Palette ===

 1. Dark Gray            - #4e4e54
 2. Medium Gray          - #54545c
 3. Slate Gray           - #52525a
 4. Charcoal             - #3e3c3f
 5. Light Cement         - #b5a898
 6. Classic Concrete     - #8c8680
 7. Warm Beige           - #c4b5a0
 8. Cool Gray            - #9b9b9b
 9. Weathered Gray       - #a8a39e
10. Stone Gray           - #979288
11. Sandy Concrete       - #d4c8b8
12. Dusty Gray           - #b8b0a8
```

Or use a preset directly:

```bash
python concrete_texture_generator.py --preset 5 --output light_cement.png
```

### 3. Random Mode

Generate with a random color from the palette:

```bash
python concrete_texture_generator.py --random
```

### Additional Options

**Custom Dimensions:**
```bash
python concrete_texture_generator.py --color "#8C8680" --width 2048 --height 2048
```

**Reproducible Results (using seed):**
```bash
python concrete_texture_generator.py --random --seed 42 --output reproducible.png
```

**Complete Options:**
```
--color COLOR      Hex color code (e.g., "#8C8680")
--palette          Show color palette and select by number
--random           Use random color from palette
--preset PRESET    Use preset color by number (1-12)
--width WIDTH      Image width in pixels (default: 1024)
--height HEIGHT    Image height in pixels (default: 1024)
--output OUTPUT    Output file path (default: concrete_texture.png)
--seed SEED        Random seed for reproducibility
```

## Examples

### Generate Classic Concrete Texture
```bash
python concrete_texture_generator.py --preset 6 --width 1024 --height 1024
```

### Create Large Light Cement Texture
```bash
python concrete_texture_generator.py --preset 5 --width 2048 --height 2048 --output cement_wall.png
```

### Use Custom Color
```bash
python concrete_texture_generator.py --color "#A5968A" --output custom_concrete.png
```

### Random Texture for Testing
```bash
python concrete_texture_generator.py --random --width 512 --height 512
```

## Color Extraction Utility

The `extract_colors.py` script was used to extract dominant colors from the reference images:

```bash
python extract_colors.py
```

This utility:
- Analyzes `Picture1.png` and `Picture2.jpg`
- Extracts images from the first slide of `ye.pptx`
- Identifies dominant colors from all sources
- Outputs RGB values and hex codes

## Dependencies

- **Pillow (PIL)** — Image processing and manipulation
- **NumPy** — Numerical operations for texture generation
- **opensimplex** — Perlin/Simplex noise generation
- **python-pptx** — PowerPoint file parsing

See `requirements.txt` for specific versions.

## Project Structure

```
concrete-texture-creator/
├── concrete_texture_generator.py  # Main texture generator script
├── extract_colors.py              # Color extraction utility
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── Picture1.png                   # Reference concrete sample
├── Picture2.jpg                   # Reference concrete sample
└── ye.pptx                        # PowerPoint with concrete samples
```

## How It Works

The generator builds the texture in layers:

1. **Base Color** — Fills the canvas with the selected concrete color
2. **Simplex Noise** — Adds organic, large-scale tonal variation using Perlin/Simplex noise
3. **Fine Grain** — Applies per-pixel random noise for sandy texture
4. **Speckles** — Randomly places darker and lighter spots to simulate aggregate
5. **Color Variation** — Uses low-frequency noise to create subtle staining effects
6. **Cracks** — Draws thin, meandering lines to simulate hairline fractures
7. **Pores** — Adds small dark dots to simulate air bubbles
8. **Dust Haze** — Applies semi-transparent white patches for a dusty appearance

Each layer is implemented as a separate function, making it easy to adjust parameters or remove effects.

## Customization

All texture parameters are defined in the `generate_concrete_texture()` function. You can modify:

- **Noise scale and intensity** — `apply_simplex_noise(scale=0.01, intensity=15)`
- **Grain intensity** — `apply_fine_grain(intensity=8)`
- **Speckle count and size** — `apply_speckles(count=500, min_size=1, max_size=4)`
- **Crack count** — `apply_cracks(count=20)`
- **Pore density** — `apply_pores(count=300, size_range=(1, 2))`
- **Staining intensity** — `apply_color_variation(intensity=20)`
- **Dust coverage** — `apply_dust_haze(patch_count=15)`

## License

This project is open source and available for use in any project.

## Contributing

Feel free to open issues or submit pull requests with improvements!

## Credits

Color palette inspired by real concrete samples provided in the reference images (`Picture1.png`, `Picture2.jpg`, and `ye.pptx`).
