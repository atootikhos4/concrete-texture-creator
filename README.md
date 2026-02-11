# Concrete Texture Generator

A Python-based procedural texture generator that creates realistic **spray-on concrete resurfacing** textures with natural imperfections. Features both a **GUI application** and **command-line interface**. The color palette is inspired by real concrete samples from the reference images included in this repository.

## Features

### GUI Application (`concrete_texture_app.py`)

The Tkinter-based GUI provides an interactive, real-time texture creation experience:

- **Live Preview Canvas** — Real-time preview (512x512) that updates as you adjust parameters
- **Color Picker** — Hex input field, color chooser dialog, and 12 preset color buttons
- **Parameter Sliders** — Fine control over all texture parameters:
  - Roughness / Grain Intensity
  - Knockdown Splatter Intensity & Scale
  - Pitting Density & Size
  - Aggregate Density
  - Crack Density
  - Staining Intensity
  - Noise Scale (fine to coarse)
- **Style Presets** — Quick presets: Light Smooth, Heavy Knockdown, Rough Industrial, Weathered
- **Export Functionality** — Save textures at any resolution (up to 8192x8192)
- **Randomize & Reset** — Quickly explore variations or return to defaults

### Texture Generation Engine

### Texture Generation Engine

This generator creates highly realistic spray-on concrete resurfacing textures by layering multiple effects:

1. **Base Color Fill** — Customizable base concrete color
2. **Multi-Octave Perlin/Simplex Noise** — Multiple scales of tonal variation for natural unevenness
3. **Knockdown Splatter Pattern** — THE KEY LAYER: Creates the characteristic spray-and-flatten pattern with hills and valleys
4. **Heavy Stipple/Grain** — Aggressive high-frequency per-pixel noise for gritty, sandy appearance
5. **Fine Grain Layer** — Additional texture layer for enhanced realism
6. **Pitting/Pinholes** — Small dark circular holes (1-4px radius) simulating trapped air bubbles
7. **Rough Aggregate/Embedded Stones** — Scattered spots (2-8px) with sharp contrast simulating sand grains and stone chips
8. **Surface Staining** — Irregular darker patches with HARD edges (not soft blends) simulating water marks
9. **Micro-cracks/Hairline Fractures** — Thin, jagged, meandering dark lines
10. **Dust/Efflorescence** — Subtle whitish patches for realistic finish

## Reference Images

The color palette was extracted from real **spray-on concrete resurfacing** samples:
- `Picture1.png` — Concrete color/texture sample
- `Picture2.jpg` — Concrete color/texture sample
- `ye.pptx` — PowerPoint file; the **first slide** contains actual concrete texture color samples

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

### GUI Application (Recommended)

Launch the interactive GUI application:

```bash
python concrete_texture_app.py
```

The GUI provides:
1. **Color Selection** — Type hex codes, use the color chooser, or click preset color buttons (1-12)
2. **Real-Time Preview** — See changes instantly as you adjust sliders
3. **Parameter Control** — Sliders for all texture parameters with live updates
4. **Style Presets** — One-click application of predefined concrete styles
5. **Export** — Save at any resolution with custom width/height
6. **Randomize** — Generate random variations for inspiration
7. **Reset** — Return to default settings

### Command-Line Interface

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

**Texture Control Parameters:**
```bash
# High roughness for very gritty texture
python concrete_texture_generator.py --preset 6 --roughness 1.5 --output rough_concrete.png

# Low pitting for cleaner surface
python concrete_texture_generator.py --preset 6 --pitting 0.5 --output clean_concrete.png

# Minimal cracks for newer concrete
python concrete_texture_generator.py --preset 6 --cracks 0.3 --output new_concrete.png

# Combine parameters for custom effect
python concrete_texture_generator.py --color "#8C8680" --roughness 0.8 --pitting 1.2 --cracks 0.6
```

**Reproducible Results (using seed):**
```bash
python concrete_texture_generator.py --random --seed 42 --output reproducible.png
```

**Complete Options:**
```
--color COLOR           Hex color code (e.g., "#8C8680")
--palette               Show color palette and select by number
--random                Use random color from palette
--preset PRESET         Use preset color by number (1-12)
--width WIDTH           Image width in pixels (default: 1024)
--height HEIGHT         Image height in pixels (default: 1024)
--roughness ROUGHNESS   Overall grittiness/grain intensity (0.0-2.0, default: 1.0)
--pitting PITTING       Density of pinholes (0.0-2.0, default: 1.0)
--cracks CRACKS         Micro-crack density (0.0-2.0, default: 1.0)
--output OUTPUT         Output file path (default: concrete_texture.png)
--seed SEED             Random seed for reproducibility
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
- **scipy** — Scientific computing library for Gaussian filters (used in knockdown splatter effect)
- **python-pptx** — PowerPoint file parsing for color extraction

See `requirements.txt` for specific versions.

## Project Structure

```
concrete-texture-creator/
├── concrete_texture_generator.py  # Core texture generation engine (CLI)
├── concrete_texture_app.py        # GUI application (Tkinter)
├── extract_colors.py              # Color extraction utility
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── Picture1.png                   # Reference concrete sample (color)
├── Picture2.jpg                   # Reference concrete sample (THE KEY REFERENCE)
└── ye.pptx                        # PowerPoint with concrete samples
```

## How It Works

The generator builds the texture in layers to replicate **real spray-on concrete resurfacing**:

1. **Base Color** — Fills the canvas with the selected concrete color
2. **Multi-Octave Simplex Noise** — Adds organic, large-scale and medium-scale tonal variation using Perlin/Simplex noise at multiple frequencies
3. **Knockdown Splatter Pattern** (THE KEY LAYER) — Uses thresholded random noise + Gaussian blur to create the characteristic spray-and-flatten pattern with "hills and valleys"
4. **Heavy Stipple** — Applies aggressive per-pixel random noise for visibly gritty, sandy texture
5. **Fine Grain** — Additional high-frequency noise layer for enhanced concrete aggregate appearance
6. **Pitting/Pinholes** — Randomly places small dark circular holes (1-4px radius) to simulate trapped air bubbles
7. **Rough Aggregate** — Scatters spots of varying sizes (2-8px) with sharp contrast to simulate visible sand grains and stone chips
8. **Surface Staining** — Creates irregular darker patches with HARD edges (not soft blends) using thresholded noise
9. **Micro-cracks** — Draws thin, jagged, meandering lines to simulate hairline fractures
10. **Surface Pores** — Adds additional small dark dots for air bubbles
11. **Dust/Efflorescence** — Applies subtle semi-transparent white patches for realistic finish

Each layer is implemented as a separate function, making it easy to adjust parameters or customize effects.

## Customization

### GUI Parameters

The GUI provides sliders for all parameters:
- **Roughness / Grain Intensity** (0.0-2.0) — Controls overall grittiness and grain intensity
- **Knockdown Splatter Intensity** (0.0-1.0) — THE KEY LAYER intensity
- **Knockdown Splatter Scale** (1.0-5.0) — Controls blur radius (fine to coarse)
- **Pitting Density** (0.0-2.0) — Density of pinholes/air bubbles
- **Pitting Size** (0.5-2.0) — Size multiplier for pinholes
- **Aggregate Density** (0.0-2.0) — Density of visible sand grains/stones
- **Crack Density** (0.0-2.0) — Micro-crack density
- **Staining Intensity** (0.0-2.0) — Surface staining/water marks
- **Noise Scale** (0.5-2.0) — Perlin noise scale (fine to coarse)

### CLI Parameters

All texture parameters can be controlled via CLI arguments:

- **`--roughness`** (0.0-2.0, default: 1.0) — Controls overall grittiness and grain intensity. Higher values create more aggressive stipple and more aggregate particles.
- **`--pitting`** (0.0-2.0, default: 1.0) — Controls density of pinholes and surface pores. Higher values create more visible trapped air bubbles.
- **`--cracks`** (0.0-2.0, default: 1.0) — Controls micro-crack density. Higher values add more hairline fractures.

### Function Parameters

The `generate_concrete_texture()` function accepts all parameters programmatically:

```python
from concrete_texture_generator import generate_concrete_texture

img = generate_concrete_texture(
    base_color='#8c8680',
    width=1024,
    height=1024,
    roughness=1.0,
    pitting=1.0,
    cracks=1.0,
    knockdown_intensity=0.8,
    knockdown_scale=2.5,
    pitting_size=1.0,
    aggregate_density=1.0,
    staining_intensity=1.0,
    noise_scale=1.0,
    verbose=False  # Set to False for silent operation (useful in GUI)
)
img.save('my_texture.png')
```

### Individual Layer Functions

Each texture layer is implemented as a separate function, making it easy to adjust or customize:

## License

This project is open source and available for use in any project.

## Contributing

Feel free to open issues or submit pull requests with improvements!

## Credits

This texture generator replicates **real spray-on concrete resurfacing** textures with characteristics like:
- Knockdown/splatter pattern from spray application
- Stippled, speckled surface with visible grain
- Pitting and pinholes from trapped air
- Rough aggregate particles and embedded stones
- Harsh, gritty industrial appearance with matte finish

Color palette inspired by real concrete samples provided in the reference images (`Picture1.png`, `Picture2.jpg`, and `ye.pptx`).
