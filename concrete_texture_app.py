#!/usr/bin/env python3
"""
Concrete Texture Generator - GUI Application

Interactive Tkinter-based GUI for creating realistic spray-on concrete resurfacing textures.
Features live preview, parameter sliders, color picker, presets, and export functionality.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
from concrete_texture_generator import (
    generate_concrete_texture, CONCRETE_PALETTE, hex_to_rgb, rgb_to_hex
)


class ConcreteTextureApp:
    """GUI application for concrete texture generation."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Concrete Texture Generator")
        self.root.geometry("1200x800")
        
        # Current parameters
        self.params = {
            'color': '#8c8680',  # Default: Classic Concrete
            'roughness': 1.0,
            'knockdown_intensity': 0.8,
            'knockdown_scale': 2.5,
            'pitting': 1.0,
            'pitting_size': 1.0,
            'aggregate_density': 1.0,
            'crack_density': 1.0,
            'staining_intensity': 1.0,
            'noise_scale': 1.0,
        }
        
        # Preview settings
        self.preview_size = 512
        self.current_preview = None
        self.generation_pending = False
        self.last_generation_time = 0
        self.debounce_delay = 0.3  # seconds
        
        # Build UI
        self.create_ui()
        
        # Generate initial preview
        self.root.after(100, self.generate_preview)
    
    def create_ui(self):
        """Create the user interface."""
        # Main container with two columns
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Left column: Preview canvas
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        preview_label = ttk.Label(left_frame, text="Live Preview", font=('Arial', 14, 'bold'))
        preview_label.pack(pady=5)
        
        # Canvas for texture preview
        self.canvas = tk.Canvas(left_frame, width=self.preview_size, height=self.preview_size, 
                               bg='#e0e0e0', highlightthickness=1, highlightbackground='#888')
        self.canvas.pack(pady=5)
        
        # Status label
        self.status_label = ttk.Label(left_frame, text="Ready", foreground='green')
        self.status_label.pack(pady=5)
        
        # Right column: Controls
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Make columns expandable
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create scrollable frame for controls
        canvas_scroll = tk.Canvas(right_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas_scroll.yview)
        scrollable_frame = ttk.Frame(canvas_scroll)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        
        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Controls title
        controls_title = ttk.Label(scrollable_frame, text="Texture Controls", 
                                   font=('Arial', 14, 'bold'))
        controls_title.pack(pady=10)
        
        # Color picker section
        self.create_color_picker(scrollable_frame)
        
        # Parameter sliders
        self.create_sliders(scrollable_frame)
        
        # Preset buttons
        self.create_presets(scrollable_frame)
        
        # Action buttons
        self.create_action_buttons(scrollable_frame)
    
    def create_color_picker(self, parent):
        """Create color picker controls."""
        color_frame = ttk.LabelFrame(parent, text="Base Color", padding="10")
        color_frame.pack(fill='x', padx=10, pady=5)
        
        # Hex input
        hex_frame = ttk.Frame(color_frame)
        hex_frame.pack(fill='x', pady=5)
        
        ttk.Label(hex_frame, text="Hex Color:").pack(side='left', padx=5)
        self.color_entry = ttk.Entry(hex_frame, width=10)
        self.color_entry.insert(0, self.params['color'])
        self.color_entry.pack(side='left', padx=5)
        self.color_entry.bind('<Return>', lambda e: self.update_color_from_entry())
        
        ttk.Button(hex_frame, text="Apply", command=self.update_color_from_entry).pack(side='left', padx=5)
        
        # Color chooser button
        ttk.Button(color_frame, text="Choose Color...", 
                  command=self.choose_color).pack(pady=5)
        
        # Color preview swatch
        self.color_swatch = tk.Canvas(color_frame, width=100, height=30, 
                                     highlightthickness=1, highlightbackground='#888')
        self.color_swatch.pack(pady=5)
        self.update_color_swatch()
        
        # Preset color buttons
        preset_frame = ttk.Frame(color_frame)
        preset_frame.pack(fill='x', pady=5)
        
        ttk.Label(preset_frame, text="Presets:").pack(anchor='w', pady=2)
        
        # Create grid of color preset buttons
        preset_grid = ttk.Frame(preset_frame)
        preset_grid.pack(fill='x')
        
        row = 0
        col = 0
        for num, info in sorted(CONCRETE_PALETTE.items()):
            btn = tk.Button(preset_grid, text=str(num), bg=info['color'],
                           width=3, height=1,
                           command=lambda c=info['color'], n=info['name']: self.set_preset_color(c, n))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            # Create tooltip
            self.create_tooltip(btn, info['name'])
            
            col += 1
            if col >= 6:
                col = 0
                row += 1
    
    def create_sliders(self, parent):
        """Create parameter sliders."""
        sliders_frame = ttk.LabelFrame(parent, text="Texture Parameters", padding="10")
        sliders_frame.pack(fill='x', padx=10, pady=5)
        
        self.sliders = {}
        
        # Define slider configurations
        slider_configs = [
            ('roughness', 'Roughness / Grain Intensity', 0.0, 2.0, 1.0),
            ('knockdown_intensity', 'Knockdown Splatter Intensity', 0.0, 1.0, 0.8),
            ('knockdown_scale', 'Knockdown Splatter Scale', 1.0, 5.0, 2.5),
            ('pitting', 'Pitting Density', 0.0, 2.0, 1.0),
            ('pitting_size', 'Pitting Size', 0.5, 2.0, 1.0),
            ('aggregate_density', 'Aggregate Density', 0.0, 2.0, 1.0),
            ('crack_density', 'Crack Density', 0.0, 2.0, 1.0),
            ('staining_intensity', 'Staining Intensity', 0.0, 2.0, 1.0),
            ('noise_scale', 'Noise Scale (Fine to Coarse)', 0.5, 2.0, 1.0),
        ]
        
        for param_name, label, min_val, max_val, default in slider_configs:
            frame = ttk.Frame(sliders_frame)
            frame.pack(fill='x', pady=3)
            
            # Label
            ttk.Label(frame, text=label, width=30, anchor='w').pack(side='left')
            
            # Value label
            value_label = ttk.Label(frame, text=f"{default:.2f}", width=6, anchor='e')
            value_label.pack(side='right', padx=5)
            
            # Slider
            slider = ttk.Scale(frame, from_=min_val, to=max_val, orient='horizontal',
                             command=lambda v, pn=param_name, vl=value_label: self.on_slider_change(pn, v, vl))
            slider.set(default)
            slider.pack(side='right', fill='x', expand=True, padx=5)
            
            self.sliders[param_name] = (slider, value_label)
    
    def create_presets(self, parent):
        """Create preset style buttons."""
        presets_frame = ttk.LabelFrame(parent, text="Style Presets", padding="10")
        presets_frame.pack(fill='x', padx=10, pady=5)
        
        # Define presets
        presets = {
            'Light Smooth': {
                'roughness': 0.5,
                'knockdown_intensity': 0.5,
                'knockdown_scale': 3.0,
                'pitting': 0.5,
                'pitting_size': 0.8,
                'aggregate_density': 0.5,
                'crack_density': 0.3,
                'staining_intensity': 0.5,
                'noise_scale': 1.2,
            },
            'Heavy Knockdown': {
                'roughness': 1.5,
                'knockdown_intensity': 1.0,
                'knockdown_scale': 2.0,
                'pitting': 1.2,
                'pitting_size': 1.3,
                'aggregate_density': 1.5,
                'crack_density': 1.0,
                'staining_intensity': 1.2,
                'noise_scale': 0.8,
            },
            'Rough Industrial': {
                'roughness': 2.0,
                'knockdown_intensity': 0.9,
                'knockdown_scale': 2.5,
                'pitting': 1.5,
                'pitting_size': 1.5,
                'aggregate_density': 2.0,
                'crack_density': 1.5,
                'staining_intensity': 1.5,
                'noise_scale': 1.0,
            },
            'Weathered': {
                'roughness': 1.2,
                'knockdown_intensity': 0.7,
                'knockdown_scale': 3.5,
                'pitting': 1.8,
                'pitting_size': 1.8,
                'aggregate_density': 1.0,
                'crack_density': 2.0,
                'staining_intensity': 2.0,
                'noise_scale': 1.5,
            },
        }
        
        for i, (name, params) in enumerate(presets.items()):
            row = i // 2
            col = i % 2
            btn = ttk.Button(presets_frame, text=name, 
                           command=lambda p=params: self.apply_preset(p))
            btn.grid(row=row, column=col, padx=5, pady=3, sticky='ew')
        
        presets_frame.columnconfigure(0, weight=1)
        presets_frame.columnconfigure(1, weight=1)
    
    def create_action_buttons(self, parent):
        """Create action buttons."""
        actions_frame = ttk.LabelFrame(parent, text="Actions", padding="10")
        actions_frame.pack(fill='x', padx=10, pady=5)
        
        # Export button
        ttk.Button(actions_frame, text="💾 Save As PNG...", 
                  command=self.export_texture).pack(fill='x', pady=3)
        
        # Randomize button
        ttk.Button(actions_frame, text="🎲 Randomize", 
                  command=self.randomize_parameters).pack(fill='x', pady=3)
        
        # Reset button
        ttk.Button(actions_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_parameters).pack(fill='x', pady=3)
    
    def create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget."""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = ttk.Label(tooltip, text=text, background="#ffffe0", 
                            relief='solid', borderwidth=1, padding=5)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def update_color_from_entry(self):
        """Update color from hex entry field."""
        hex_color = self.color_entry.get().strip()
        if not hex_color.startswith('#'):
            hex_color = '#' + hex_color
        
        # Validate hex color
        try:
            hex_to_rgb(hex_color)
            self.params['color'] = hex_color
            self.update_color_swatch()
            self.schedule_generation()
        except:
            messagebox.showerror("Invalid Color", "Please enter a valid hex color code (e.g., #8C8680)")
    
    def choose_color(self):
        """Open color chooser dialog."""
        color = colorchooser.askcolor(initialcolor=self.params['color'])
        if color[1]:  # color[1] is the hex string
            self.params['color'] = color[1]
            self.color_entry.delete(0, tk.END)
            self.color_entry.insert(0, color[1])
            self.update_color_swatch()
            self.schedule_generation()
    
    def set_preset_color(self, color, name):
        """Set a preset color."""
        self.params['color'] = color
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, color)
        self.update_color_swatch()
        self.status_label.config(text=f"Color: {name}")
        self.schedule_generation()
    
    def update_color_swatch(self):
        """Update the color preview swatch."""
        self.color_swatch.delete('all')
        self.color_swatch.create_rectangle(0, 0, 100, 30, 
                                          fill=self.params['color'], outline='#888')
    
    def on_slider_change(self, param_name, value, value_label):
        """Handle slider value changes."""
        float_val = float(value)
        self.params[param_name] = float_val
        value_label.config(text=f"{float_val:.2f}")
        self.schedule_generation()
    
    def apply_preset(self, params):
        """Apply a preset configuration."""
        for param_name, value in params.items():
            self.params[param_name] = value
            if param_name in self.sliders:
                slider, value_label = self.sliders[param_name]
                slider.set(value)
                value_label.config(text=f"{value:.2f}")
        
        self.schedule_generation()
    
    def randomize_parameters(self):
        """Randomize all parameters."""
        import random
        
        # Randomize color
        color_num = random.choice(list(CONCRETE_PALETTE.keys()))
        self.set_preset_color(CONCRETE_PALETTE[color_num]['color'], 
                             CONCRETE_PALETTE[color_num]['name'])
        
        # Randomize sliders
        for param_name, (slider, value_label) in self.sliders.items():
            from_val = slider.cget('from')
            to_val = slider.cget('to')
            rand_val = random.uniform(float(from_val), float(to_val))
            slider.set(rand_val)
            self.params[param_name] = rand_val
            value_label.config(text=f"{rand_val:.2f}")
        
        self.schedule_generation()
    
    def reset_parameters(self):
        """Reset all parameters to defaults."""
        defaults = {
            'color': '#8c8680',
            'roughness': 1.0,
            'knockdown_intensity': 0.8,
            'knockdown_scale': 2.5,
            'pitting': 1.0,
            'pitting_size': 1.0,
            'aggregate_density': 1.0,
            'crack_density': 1.0,
            'staining_intensity': 1.0,
            'noise_scale': 1.0,
        }
        
        self.params.update(defaults)
        
        # Update color entry
        self.color_entry.delete(0, tk.END)
        self.color_entry.insert(0, defaults['color'])
        self.update_color_swatch()
        
        # Update sliders
        for param_name, (slider, value_label) in self.sliders.items():
            value = defaults[param_name]
            slider.set(value)
            value_label.config(text=f"{value:.2f}")
        
        self.schedule_generation()
    
    def schedule_generation(self):
        """Schedule texture generation with debouncing."""
        self.generation_pending = True
        current_time = time.time()
        
        # If enough time has passed, generate immediately
        if current_time - self.last_generation_time >= self.debounce_delay:
            self.root.after(100, self.check_and_generate)
        else:
            # Schedule check after debounce delay
            self.root.after(int(self.debounce_delay * 1000), self.check_and_generate)
    
    def check_and_generate(self):
        """Check if generation is still pending and execute if so."""
        if self.generation_pending:
            self.generation_pending = False
            self.generate_preview()
    
    def generate_preview(self):
        """Generate texture preview in a background thread."""
        self.status_label.config(text="Generating...", foreground='orange')
        self.root.update()
        
        # Start generation in thread
        thread = threading.Thread(target=self._generate_preview_thread, daemon=True)
        thread.start()
    
    def _generate_preview_thread(self):
        """Background thread for texture generation."""
        try:
            # Generate texture
            img = generate_concrete_texture(
                base_color=self.params['color'],
                width=self.preview_size,
                height=self.preview_size,
                roughness=self.params['roughness'],
                pitting=self.params['pitting'],
                cracks=self.params['crack_density'],
                knockdown_intensity=self.params['knockdown_intensity'],
                knockdown_scale=self.params['knockdown_scale'],
                pitting_size=self.params['pitting_size'],
                aggregate_density=self.params['aggregate_density'],
                staining_intensity=self.params['staining_intensity'],
                noise_scale=self.params['noise_scale'],
                verbose=False
            )
            
            # Store for export
            self.current_preview = img
            
            # Update UI on main thread
            self.root.after(0, self._update_preview_display, img)
            self.last_generation_time = time.time()
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
    
    def _update_preview_display(self, img):
        """Update the preview display (must run on main thread)."""
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Update canvas
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=photo)
        self.canvas.image = photo  # Keep reference
        
        self.status_label.config(text="Ready", foreground='green')
    
    def _show_error(self, error_msg):
        """Show error message (must run on main thread)."""
        self.status_label.config(text=f"Error: {error_msg}", foreground='red')
        messagebox.showerror("Generation Error", f"Failed to generate texture:\n{error_msg}")
    
    def export_texture(self):
        """Export texture at full resolution."""
        # Ask for dimensions
        export_dialog = tk.Toplevel(self.root)
        export_dialog.title("Export Texture")
        export_dialog.geometry("300x150")
        export_dialog.transient(self.root)
        export_dialog.grab_set()
        
        ttk.Label(export_dialog, text="Export Dimensions:").pack(pady=10)
        
        dim_frame = ttk.Frame(export_dialog)
        dim_frame.pack(pady=5)
        
        ttk.Label(dim_frame, text="Width:").grid(row=0, column=0, padx=5)
        width_entry = ttk.Entry(dim_frame, width=10)
        width_entry.insert(0, "1024")
        width_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(dim_frame, text="Height:").grid(row=1, column=0, padx=5, pady=5)
        height_entry = ttk.Entry(dim_frame, width=10)
        height_entry.insert(0, "1024")
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def do_export():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())
                
                if width < 64 or height < 64 or width > 8192 or height > 8192:
                    messagebox.showerror("Invalid Dimensions", 
                                       "Width and height must be between 64 and 8192 pixels.")
                    return
                
                export_dialog.destroy()
                self._export_with_dimensions(width, height)
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter valid integer dimensions.")
        
        ttk.Button(export_dialog, text="Export", command=do_export).pack(pady=10)
    
    def _export_with_dimensions(self, width, height):
        """Export texture with specified dimensions."""
        # Ask for filename
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            title="Save Texture As"
        )
        
        if not filename:
            return
        
        # Show progress
        self.status_label.config(text="Exporting...", foreground='orange')
        self.root.update()
        
        # Generate full-resolution texture
        try:
            img = generate_concrete_texture(
                base_color=self.params['color'],
                width=width,
                height=height,
                roughness=self.params['roughness'],
                pitting=self.params['pitting'],
                cracks=self.params['crack_density'],
                knockdown_intensity=self.params['knockdown_intensity'],
                knockdown_scale=self.params['knockdown_scale'],
                pitting_size=self.params['pitting_size'],
                aggregate_density=self.params['aggregate_density'],
                staining_intensity=self.params['staining_intensity'],
                noise_scale=self.params['noise_scale'],
                verbose=True  # Show progress in console
            )
            
            img.save(filename)
            self.status_label.config(text=f"Exported to {filename}", foreground='green')
            messagebox.showinfo("Export Successful", 
                              f"Texture saved successfully to:\n{filename}\n({width}x{height} pixels)")
            
        except Exception as e:
            self.status_label.config(text="Export failed", foreground='red')
            messagebox.showerror("Export Error", f"Failed to export texture:\n{str(e)}")


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = ConcreteTextureApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
