import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
from video_capture import *
from image_capture import *
from advanced_filters import AdvancedFilters
from batch_processor import BatchProcessor
import PIL

# create folder directory to save images
folder = r"\images"
cwd = os.getcwd()
path = cwd + folder
if not os.path.exists(path):
    os.makedirs(path)

# create a dictionary for the filters
fil = ['color', 'gray', 'threshold', 'increaseContrast', 'decreaseContrast', 
       'logTransformation', 'powerLowEnhancement', 'negativeEnhancement', 
       'gauss', 'sobel', 'laplace', 'min', 'max', 'median', 'average', 
       'unsharp', 'prewitt', 'histogramEqualization', 'sepia', 'vintage',
       'vignette', 'temperature', 'saturation', 'denoise', 'hdr', 'tilt_shift']

def select_filter(filter, status):
    filter_dic = {x: False for x in fil}
    if filter in filter_dic:
        assert type(status) == bool
        filter_dic[filter] = status
    return filter_dic

class FiltrawyApp:
    def __init__(self, window):
        self.window = window
        self.window.title("GREAT MATES - Computer Science")
        self.window.geometry("1400x900")
        
        # Initialize filter parameters
        self.filter_params = {
            'intensity': tk.DoubleVar(value=1.0),
            'threshold': tk.IntVar(value=127),
            'blur_radius': tk.IntVar(value=5),
            'temperature': tk.IntVar(value=0),
            'saturation': tk.DoubleVar(value=1.0),
            'vignette': tk.DoubleVar(value=0.5)
        }
        
        # Load logo
        try:
            logo_path = os.path.join("test-images", "greatmates_logo.png")
            logo_image = PIL.Image.open(logo_path)
            logo_image = logo_image.resize((150, 150), PIL.Image.LANCZOS)
            self.logo_photo = PIL.ImageTk.PhotoImage(logo_image)
        except Exception as e:
            print(f"Could not load logo: {str(e)}")
            self.logo_photo = None
        
        # Create style
        self.create_styles()
        
        # Create main containers
        self.create_layout()
        
        # Initialize image capture and batch processor
        self.img = None
        self.batch_processor = None
        
        # Create keyboard shortcuts
        self.create_shortcuts()
    
    def create_shortcuts(self):
        self.window.bind('<Control-o>', lambda e: self.select_image())
        self.window.bind('<Control-s>', lambda e: self.save_image())
        self.window.bind('<Control-z>', lambda e: self.undo())
        self.window.bind('<Control-y>', lambda e: self.redo())
        self.window.bind('<Control-r>', lambda e: self.reset_image())
        self.window.bind('<Control-plus>', lambda e: self.zoom(1.2))
        self.window.bind('<Control-minus>', lambda e: self.zoom(0.8))
    
    def create_styles(self):
        style = ttk.Style()
        
        # Configure modern button style
        style.configure("Filter.TButton", 
                      padding=5,
                      font=('Helvetica', 9),
                      width=20)  # Fixed width for filter buttons
        
        style.configure("Action.TButton",
                      padding=8,
                      font=('Helvetica', 10, 'bold'))
        
        style.configure("Category.TLabel", 
                      font=('Helvetica', 11, 'bold'),
                      foreground='#2c3e50',
                      padding=(5, 10, 5, 5))
        
        style.configure("Control.TFrame", padding=5)
        
        # Configure logo styles
        style.configure("Logo.TFrame", padding=10)
        style.configure("Logo.TLabel", padding=5)
        style.configure("AppName.TLabel", 
                      foreground="#2c3e50",
                      padding=5,
                      font=('Helvetica', 28, 'bold'))
        
        style.configure("Subtitle.TLabel",
                      foreground="#7f8c8d",
                      padding=5,
                      font=('Helvetica', 14))
        
        # Configure modern control styles
        style.configure("Controls.TFrame", padding=10)
        style.configure("Controls.TLabel", font=('Helvetica', 9))
        style.configure("Controls.TScale", sliderlength=20)
        
        # Configure filter frame style
        style.configure("Filters.TLabelframe",
                      padding=10,
                      relief="flat",
                      borderwidth=0)
        
        style.configure("Filters.TLabelframe.Label",
                      font=('Helvetica', 12, 'bold'),
                      foreground='#2c3e50')
    
    def create_layout(self):
        # Create menu bar first
        self.create_menu()
        
        # Create main frames
        # Filter frame on the left - starts from row 0 (menu bar level)
        self.filter_frame = ttk.LabelFrame(self.window, text="Filters")
        self.filter_frame.grid(row=0, column=0, rowspan=4, sticky="nsew", padx=10, pady=5)
        
        # Top frame for logo and title - row 0, starts from column 1
        self.top_frame = ttk.Frame(self.window)
        self.top_frame.grid(row=0, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Create logo frame in center
        logo_frame = ttk.Frame(self.top_frame)
        logo_frame.pack(expand=True, fill="both")
        
        # Add logo if available
        if hasattr(self, 'logo_photo') and self.logo_photo:
            # Create a stylish container for the logo
            logo_container = ttk.Frame(logo_frame, style="Logo.TFrame")
            logo_container.pack(anchor="center", pady=10)
            
            # Add logo with a modern border
            logo_label = ttk.Label(logo_container, image=self.logo_photo, 
                                 style="Logo.TLabel")
            logo_label.pack(side="top", padx=20)
            
            # Add app name with modern styling
            app_name = ttk.Label(logo_container, text="GREAT MATES", 
                               font=('Helvetica', 28, 'bold'),
                               style="AppName.TLabel")
            app_name.pack(side="top", pady=(5,0))
            
            # Add subtitle with modern styling
            subtitle = ttk.Label(logo_container, text="Computer Science", 
                               font=('Helvetica', 14),
                               style="Subtitle.TLabel")
            subtitle.pack(side="top", pady=(0,5))
        
        # Add top buttons below logo
        self.create_top_buttons()
        
        # Control frame below logo
        self.control_frame = ttk.LabelFrame(self.window, text="Filter Controls")
        self.control_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Image display area - centered under controls
        self.display_frame = ttk.Frame(self.window, name="display_frame")
        self.display_frame.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        # Add image display labels in a single row
        self.original_label_frame = ttk.LabelFrame(self.display_frame, text="Original Image")
        self.original_label_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        
        self.filtered_label_frame = ttk.LabelFrame(self.display_frame, text="Filtered Image")
        self.filtered_label_frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        
        # Create filter categories
        self.create_filter_categories()
        
        # Create filter controls
        self.create_filter_controls()
        
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=0)  # Logo row - fixed height
        self.window.grid_rowconfigure(1, weight=0)  # Controls row - fixed height
        self.window.grid_rowconfigure(2, weight=1)  # Image display row - expandable
        
        self.window.grid_columnconfigure(0, weight=0)  # Filter column - fixed width
        self.window.grid_columnconfigure(1, weight=1)  # Main content column - expandable
        self.window.grid_columnconfigure(2, weight=1)  # Main content column - expandable
        
        # Make filter frame fixed width and full height
        self.filter_frame.grid_propagate(False)
        self.filter_frame.configure(width=200)  # Fixed width for filter panel
    
    def create_menu(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image", command=self.select_image)
        file_menu.add_command(label="Open Camera", command=self.select_camera)
        file_menu.add_separator()
        file_menu.add_command(label="Save Image", command=self.save_image)
        file_menu.add_command(label="Save As...", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Batch Process...", command=self.start_batch_processing)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.undo)
        edit_menu.add_command(label="Redo", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset Image", command=self.reset_image)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=lambda: self.zoom(1.2))
        view_menu.add_command(label="Zoom Out", command=lambda: self.zoom(0.8))
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window)
        
        # Filters menu
        filters_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Filters", menu=filters_menu)
        
        # Create submenus for filter categories
        categories = {
            "Basic": ['color', 'gray', 'threshold'],
            "Enhancement": ['increaseContrast', 'decreaseContrast', 'logTransformation'],
            "Effects": ['sepia', 'vintage', 'vignette']
        }
        
        for category, filters in categories.items():
            submenu = tk.Menu(filters_menu, tearoff=0)
            filters_menu.add_cascade(label=category, menu=submenu)
            for f in filters:
                submenu.add_command(label=f.capitalize(), 
                                  command=lambda x=f: self.apply_filter(x))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Start", command=self.show_quick_start)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_filter_controls(self):
        # Create a frame for each control group
        basic_controls = ttk.LabelFrame(self.control_frame, text="Basic Controls")
        basic_controls.pack(fill="x", padx=5, pady=5)
        
        color_controls = ttk.LabelFrame(self.control_frame, text="Color Controls")
        color_controls.pack(fill="x", padx=5, pady=5)
        
        effect_controls = ttk.LabelFrame(self.control_frame, text="Effect Controls")
        effect_controls.pack(fill="x", padx=5, pady=5)

        # Basic Controls
        # Intensity slider
        ttk.Label(basic_controls, text="Intensity:").pack(anchor="w", padx=5, pady=2)
        self.intensity_slider = ttk.Scale(
            basic_controls,
            from_=0.1,
            to=2.0,
            orient="horizontal",
            variable=self.filter_params['intensity']
        )
        self.intensity_slider.pack(fill="x", padx=5, pady=2)
        
        # Threshold slider
        ttk.Label(basic_controls, text="Threshold:").pack(anchor="w", padx=5, pady=2)
        self.threshold_slider = ttk.Scale(
            basic_controls,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.filter_params['threshold']
        )
        self.threshold_slider.pack(fill="x", padx=5, pady=2)
        
        # Color Controls
        # Temperature slider
        ttk.Label(color_controls, text="Temperature:").pack(anchor="w", padx=5, pady=2)
        self.temp_slider = ttk.Scale(
            color_controls,
            from_=-50,
            to=50,
            orient="horizontal",
            variable=self.filter_params['temperature']
        )
        self.temp_slider.pack(fill="x", padx=5, pady=2)
        
        # Saturation slider
        ttk.Label(color_controls, text="Saturation:").pack(anchor="w", padx=5, pady=2)
        self.sat_slider = ttk.Scale(
            color_controls,
            from_=0.0,
            to=2.0,
            orient="horizontal",
            variable=self.filter_params['saturation']
        )
        self.sat_slider.pack(fill="x", padx=5, pady=2)
        
        # Effect Controls
        # Vignette slider
        ttk.Label(effect_controls, text="Vignette:").pack(anchor="w", padx=5, pady=2)
        self.vignette_slider = ttk.Scale(
            effect_controls,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            variable=self.filter_params['vignette']
        )
        self.vignette_slider.pack(fill="x", padx=5, pady=2)
        
        # Blur radius slider
        ttk.Label(effect_controls, text="Blur Radius:").pack(anchor="w", padx=5, pady=2)
        self.blur_slider = ttk.Scale(
            effect_controls,
            from_=1,
            to=21,
            orient="horizontal",
            variable=self.filter_params['blur_radius']
        )
        self.blur_slider.pack(fill="x", padx=5, pady=2)
        
        # Bind all sliders to update function
        for slider in [self.intensity_slider, self.threshold_slider, 
                      self.temp_slider, self.sat_slider,
                      self.vignette_slider, self.blur_slider]:
            slider.configure(command=self.on_slider_change)
    
    def on_slider_change(self, value):
        if self.img and hasattr(self.img, 'update'):
            # Update filter parameters
            params = {
                'intensity': self.filter_params['intensity'].get(),
                'threshold': self.filter_params['threshold'].get(),
                'temperature': self.filter_params['temperature'].get(),
                'saturation': self.filter_params['saturation'].get(),
                'vignette': self.filter_params['vignette'].get(),
                'blur_radius': self.filter_params['blur_radius'].get()
            }
            # Pass parameters to image processor
            if hasattr(self.img, 'set_filter_params'):
                self.img.set_filter_params(params)
            self.img.update()
    
    def save_image(self):
        if hasattr(self.img, 'save_image'):
            self.img.save_image()
    
    def save_image_as(self):
        if not hasattr(self.img, 'filtered_image'):
            messagebox.showwarning("Warning", "No image to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                cv2.imwrite(file_path, cv2.cvtColor(self.img.filtered_image, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Success", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def undo(self):
        if hasattr(self.img, 'undo'):
            self.img.undo()
    
    def redo(self):
        if hasattr(self.img, 'redo'):
            self.img.redo()
    
    def reset_image(self):
        if hasattr(self.img, 'reset'):
            self.img.reset()
    
    def zoom(self, factor):
        if hasattr(self.img, 'zoom'):
            self.img.zoom(factor)
    
    def fit_to_window(self):
        if hasattr(self.img, 'fit_to_window'):
            self.img.fit_to_window()
    
    def show_quick_start(self):
        quick_start_text = """Quick Start Guide:

1. Open an image:
   - Click 'File > Open Image' or use the Open Image button
   - Select an image file from your computer

2. Apply filters:
   - Choose a filter from the left panel
   - Adjust filter settings using the sliders
   - Use Undo/Redo to navigate through changes

3. Save your work:
   - Click 'File > Save' to save changes
   - Use 'File > Save As' to save as a new file

4. Batch Processing:
   - Use 'File > Batch Process' to apply filters to multiple images
   - Select input and output folders
   - Choose a filter to apply to all images"""
        
        messagebox.showinfo("Quick Start Guide", quick_start_text)
    
    def show_shortcuts(self):
        shortcuts_text = """Keyboard Shortcuts:

File Operations:
Ctrl+O : Open Image
Ctrl+S : Save
Ctrl+Shift+S : Save As
Ctrl+B : Batch Process
Ctrl+Q : Quit

Edit Operations:
Ctrl+Z : Undo
Ctrl+Y : Redo
Ctrl+R : Reset Image

View Operations:
Ctrl++ : Zoom In
Ctrl+- : Zoom Out
Ctrl+0 : Fit to Window"""
        
        messagebox.showinfo("Keyboard Shortcuts", shortcuts_text)
    
    def create_top_buttons(self):
        # Create a frame for buttons
        button_frame = ttk.Frame(self.top_frame)
        button_frame.pack(fill="x", padx=20, pady=(0,10))
        
        # Center the buttons
        button_container = ttk.Frame(button_frame)
        button_container.pack(anchor="center")
        
        # Add modern-styled buttons
        ttk.Button(button_container, text="Open Image", 
                  style="Action.TButton",
                  command=self.select_image).pack(side="left", padx=5)
        ttk.Button(button_container, text="Open Camera",
                  style="Action.TButton", 
                  command=self.select_camera).pack(side="left", padx=5)
        ttk.Button(button_container, text="Batch Process",
                  style="Action.TButton",
                  command=self.start_batch_processing).pack(side="left", padx=5)
    
    def create_filter_categories(self):
        # Configure filter frame style
        self.filter_frame.configure(style="Filters.TLabelframe")
        
        categories = {
            "Basic": ['color', 'gray', 'threshold'],
            "Enhancement": ['increaseContrast', 'decreaseContrast', 'logTransformation', 
                          'powerLowEnhancement', 'negativeEnhancement'],
            "Blur": ['gauss', 'median', 'average'],
            "Edge Detection": ['sobel', 'laplace', 'prewitt'],
            "Morphological": ['min', 'max'],
            "Advanced": ['unsharp', 'histogramEqualization'],
            "Instagram Style": ['sepia', 'vintage', 'vignette', 'temperature', 'saturation'],
            "Special Effects": ['denoise', 'hdr', 'tilt_shift']
        }
        
        # Create a canvas with scrollbar for the filter categories
        canvas = tk.Canvas(self.filter_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.filter_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_reqwidth())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(5,0))
        scrollbar.pack(side="right", fill="y")
        
        row = 0
        for category, filters in categories.items():
            # Add category label
            ttk.Label(scrollable_frame, text=category, style="Category.TLabel").grid(
                row=row, column=0, sticky="w", padx=5, pady=(10,5))
            row += 1
            
            # Add filter buttons
            for filter_name in filters:
                btn = ttk.Button(scrollable_frame, text=filter_name.capitalize(),
                               style="Filter.TButton",
                               command=lambda f=filter_name: self.apply_filter(f))
                btn.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
                self.create_tooltip(btn, f"Apply {filter_name} filter")
                row += 1
        
        # Configure scrollable_frame grid
        scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = ttk.Label(self.tooltip, text=text, background="#ffffe0", 
                            relief='solid', borderwidth=1)
            label.pack()
        
        def hide_tooltip(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
    
    def show_about(self):
        about_text = """Filtrawy - Advanced Image Processing Application
        
Version: 3.0
Created by: Great Mates

Features:
- 25+ image processing filters
- Real-time camera processing
- Batch processing
- Instagram-style filters
- Modern user interface

Thank you for using Filtrawy!"""
        
        messagebox.showinfo("About Filtrawy", about_text)
    
    def select_image(self):
        try:
            self.img = ImageCap(self.window)
            # Update window title with image name if available
            if hasattr(self.img, 'filename'):
                filename = os.path.basename(self.img.filename)
                self.window.title(f"GREAT MATES - Computer Science - {filename}")
            else:
                self.window.title("GREAT MATES - Computer Science")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {str(e)}")
    
    def select_camera(self):
        try:
            self.img = VideoCap(self.window)
            self.window.title("GREAT MATES - Computer Science - Camera Feed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open camera: {str(e)}")
    
    def apply_filter(self, filter_name):
        if self.img is None:
            messagebox.showwarning("Warning", "Please open an image or camera first!")
            return
        
        try:
            # Reset all filters
            self.img.all_filters = {f: False for f in fil}
            # Enable selected filter
            self.img.all_filters[filter_name] = True
            # Update filter parameters
            if hasattr(self.img, 'set_filter_params'):
                self.img.set_filter_params({
                    'intensity': self.filter_params['intensity'].get(),
                    'threshold': self.filter_params['threshold'].get(),
                    'temperature': self.filter_params['temperature'].get(),
                    'saturation': self.filter_params['saturation'].get(),
                    'vignette': self.filter_params['vignette'].get(),
                    'blur_radius': self.filter_params['blur_radius'].get()
                })
            # Apply filter
            self.img.update()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filter: {str(e)}")
    
    def start_batch_processing(self):
        input_dir = filedialog.askdirectory(title="Select Input Directory")
        if not input_dir:
            return
            
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return
        
        self.batch_processor = BatchProcessor(input_dir, output_dir)
        
        # Create dialog for batch processing options
        dialog = tk.Toplevel(self.window)
        dialog.title("Batch Processing")
        dialog.geometry("300x400")
        
        ttk.Label(dialog, text="Select Filter:").pack(pady=5)
        filter_var = tk.StringVar(value="sepia")
        filter_combo = ttk.Combobox(dialog, textvariable=filter_var, values=fil)
        filter_combo.pack(pady=5)
        
        ttk.Button(dialog, text="Start Processing",
                  command=lambda: self.run_batch_process(filter_var.get(), dialog)).pack(pady=10)
    
    def run_batch_process(self, filter_name, dialog):
        dialog.destroy()
        
        # Show progress dialog
        progress_dialog = tk.Toplevel(self.window)
        progress_dialog.title("Processing Images")
        progress_dialog.geometry("300x150")
        
        ttk.Label(progress_dialog, text="Processing images...").pack(pady=20)
        progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
        progress_bar.pack(fill='x', padx=20)
        progress_bar.start()
        
        def process():
            results = self.batch_processor.process_directory(filter_name)
            progress_dialog.destroy()
            
            # Show results
            success = sum(1 for _, status in results if status)
            messagebox.showinfo("Batch Processing Complete",
                              f"Processed {len(results)} images\n"
                              f"Successful: {success}\n"
                              f"Failed: {len(results) - success}")
        
        self.window.after(100, process)

if __name__ == '__main__':
    root = tk.Tk()
    app = FiltrawyApp(root)
    root.mainloop()
