import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.filedialog
import cv2
import PIL.Image
import PIL.ImageTk
import PIL.ImageFilter
import numpy as np
from typing import List, Dict
from advanced_filters import AdvancedFilters

class ImageCap:
    def __init__(self, window=None):
        self.window = window
        self.history: List[np.ndarray] = []
        self.history_position = -1
        self.zoom_factor = 1.0
        self.original_size = (400, 400)
        
        # Initialize filter parameters
        self.filter_params = {
            'intensity': 1.0,
            'threshold': 127,
            'temperature': 0,
            'saturation': 1.0,
            'vignette': 0.5,
            'blur_radius': 5
        }
        
        self.all_filters = {x: False for x in ['color', 'gray', 'threshold', 'increaseContrast', 
                                             'decreaseContrast', 'logTransformation', 'powerLowEnhancement',
                                             'negativeEnhancement', 'gauss', 'sobel', 'laplace', 'min',
                                             'max', 'median', 'average', 'unsharp', 'prewitt',
                                             'histogramEqualization', 'sepia', 'vintage', 'vignette',
                                             'temperature', 'saturation', 'denoise', 'hdr', 'tilt_shift']}
        
        # Initialize advanced filters
        self.advanced_filters = AdvancedFilters()
        
        # Open file dialog
        self.select_file()
    
    def set_filter_params(self, params):
        """Update filter parameters"""
        self.filter_params.update(params)
    
    def apply_filter(self, image):
        """Apply the selected filter with current parameters"""
        if image is None:
            return None
            
        # Convert to float32 for processing
        img = image.astype(np.float32) / 255.0
        
        # Apply selected filter
        for filter_name, is_active in self.all_filters.items():
            if not is_active:
                continue
                
            if filter_name == 'color':
                img = img * self.filter_params['intensity']
            elif filter_name == 'gray':
                if len(img.shape) == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                    img = np.stack([img] * 3, axis=-1)
            elif filter_name == 'threshold':
                threshold = self.filter_params['threshold'] / 255.0
                img = np.where(img > threshold, 1.0, 0.0)
            elif filter_name == 'gauss':
                kernel_size = int(self.filter_params['blur_radius'])
                if kernel_size % 2 == 0:
                    kernel_size += 1  # Ensure odd kernel size
                img = cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
            elif filter_name == 'temperature':
                temp = self.filter_params['temperature'] / 50.0  # Normalize to [-1, 1]
                if temp > 0:  # Warmer
                    img[:,:,2] = np.clip(img[:,:,2] + temp * 0.5, 0, 1)  # More red
                    img[:,:,0] = np.clip(img[:,:,0] - temp * 0.5, 0, 1)  # Less blue
                else:  # Cooler
                    img[:,:,0] = np.clip(img[:,:,0] - temp * 0.5, 0, 1)  # More blue
                    img[:,:,2] = np.clip(img[:,:,2] + temp * 0.5, 0, 1)  # Less red
            elif filter_name == 'saturation':
                if len(img.shape) == 3:
                    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
                    hsv[:,:,1] = np.clip(hsv[:,:,1] * self.filter_params['saturation'], 0, 1)
                    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            elif filter_name == 'vignette':
                strength = self.filter_params['vignette']
                rows, cols = img.shape[:2]
                # Create a vignette mask
                kernel_x = cv2.getGaussianKernel(cols, cols/4)  # Adjusted sigma for stronger effect
                kernel_y = cv2.getGaussianKernel(rows, rows/4)
                kernel = kernel_y * kernel_x.T
                mask = kernel / kernel.max()
                mask = 1 - (1 - mask) * strength
                # Apply the mask to each channel
                for i in range(3):
                    img[:,:,i] = img[:,:,i] * mask
            elif filter_name == 'increaseContrast':
                img = np.clip(img * 1.5, 0, 1)
            elif filter_name == 'decreaseContrast':
                img = np.clip(img * 0.5, 0, 1)
            elif filter_name == 'logTransformation':
                c = 1 / np.log(1 + np.max(img))
                img = c * np.log(1 + img)
            elif filter_name == 'powerLowEnhancement':
                gamma = 0.5
                img = np.power(img, gamma)
            elif filter_name == 'negativeEnhancement':
                img = 1 - img
            elif filter_name == 'sobel':
                if len(img.shape) == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)
                img = np.sqrt(sobelx**2 + sobely**2)
                img = np.stack([img] * 3, axis=-1)
            elif filter_name == 'laplace':
                if len(img.shape) == 3:
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                img = cv2.Laplacian(img, cv2.CV_64F)
                img = np.stack([img] * 3, axis=-1)
        
        # Convert back to uint8
        img = np.clip(img * 255.0, 0, 255).astype(np.uint8)
        return img

    def update(self):
        """Update the displayed image with current filters"""
        if not hasattr(self, 'original_image'):
            return
            
        # Apply filters
        self.filtered_image = self.apply_filter(self.original_image)
        
        if self.filtered_image is not None:
            # Add to history
            if self.history_position < len(self.history) - 1:
                self.history = self.history[:self.history_position + 1]
            self.history.append(self.filtered_image.copy())
            self.history_position = len(self.history) - 1
            
            # Update display
            self.show_image()
    
    def create_scrollable_frame(self, parent, row, column):
        """Create a frame with scrollbars"""
        # Create a canvas with scrollbars
        canvas = tk.Canvas(parent, borderwidth=0)
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        
        # Create the scrollable frame inside the canvas
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Add the frame to the canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Grid layout for scrollbars and canvas
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Configure parent grid weights
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Bind mouse wheel to vertical scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind shift + mouse wheel to horizontal scroll
        def _on_shift_mousewheel(event):
            canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
        
        return scrollable_frame
    
    def show_image(self):
        """Display both original and filtered images side by side with scrollbars"""
        if not hasattr(self, 'original_image') or not hasattr(self, 'filtered_image'):
            return
            
        # Resize images
        display_size = (int(self.original_size[0] * self.zoom_factor),
                       int(self.original_size[1] * self.zoom_factor))
                       
        # Process original image
        original_pil = PIL.Image.fromarray(self.original_image)
        original_pil = original_pil.resize(display_size, PIL.Image.LANCZOS)
        self.original_photo = PIL.ImageTk.PhotoImage(image=original_pil)
        
        # Process filtered image
        filtered_pil = PIL.Image.fromarray(self.filtered_image)
        filtered_pil = filtered_pil.resize(display_size, PIL.Image.LANCZOS)
        self.filtered_photo = PIL.ImageTk.PhotoImage(image=filtered_pil)
        
        # Create or update labels
        if not hasattr(self, 'original_label'):
            # Find the display frames
            original_frame = None
            filtered_frame = None
            
            for child in self.window.winfo_children():
                if str(child).endswith('display_frame'):
                    display_frame = child
                    for subchild in display_frame.winfo_children():
                        if isinstance(subchild, ttk.LabelFrame):
                            if "Original" in str(subchild):
                                original_frame = subchild
                            elif "Filtered" in str(subchild):
                                filtered_frame = subchild
            
            if not original_frame or not filtered_frame:
                return
            
            # Create scrollable frames inside the label frames
            original_scroll = self.create_scrollable_frame(original_frame, 0, 0)
            filtered_scroll = self.create_scrollable_frame(filtered_frame, 0, 0)
            
            # Create image labels inside scrollable frames
            self.original_label = ttk.Label(original_scroll, image=self.original_photo)
            self.original_label.pack(expand=True, fill="both", padx=5, pady=5)
            
            self.filtered_label = ttk.Label(filtered_scroll, image=self.filtered_photo)
            self.filtered_label.pack(expand=True, fill="both", padx=5, pady=5)
            
            # Store references to prevent garbage collection
            self.original_label.image = self.original_photo
            self.filtered_label.image = self.filtered_photo
        else:
            # Update existing labels
            self.original_label.configure(image=self.original_photo)
            self.original_label.image = self.original_photo
            self.filtered_label.configure(image=self.filtered_photo)
            self.filtered_label.image = self.filtered_photo
    
    def select_file(self):
        """Open file dialog to select an image"""
        try:
            img_path = tkinter.filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if len(img_path) > 0:
                self.filename = img_path  # Store the filename
                self.original_image = cv2.imread(img_path)
                if self.original_image is None:
                    raise ValueError("Could not load image")
                    
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.filtered_image = self.original_image.copy()
                
                # Store original size
                self.original_size = self.original_image.shape[:2][::-1]
                
                # Initialize history
                self.history = [self.original_image.copy()]
                self.history_position = 0
                
                # Show initial image
                self.show_image()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def save_image(self):
        """Save the current filtered image"""
        try:
            if hasattr(self, 'filtered_image') and self.filtered_image is not None:
                save_path = tkinter.filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
                )
                if save_path:
                    save_image = self.filtered_image
                    if len(save_image.shape) == 2:  # If grayscale
                        save_image = cv2.cvtColor(save_image, cv2.COLOR_GRAY2BGR)
                    save_image = cv2.cvtColor(save_image, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(save_path, save_image)
                    messagebox.showinfo("Success", "Image saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def undo(self):
        """Undo the last filter operation"""
        if self.history_position > 0:
            self.history_position -= 1
            self.filtered_image = self.history[self.history_position].copy()
            self.show_image()
    
    def redo(self):
        """Redo the last undone filter operation"""
        if self.history_position < len(self.history) - 1:
            self.history_position += 1
            self.filtered_image = self.history[self.history_position].copy()
            self.show_image()
    
    def reset(self):
        """Reset to original image"""
        if hasattr(self, 'original_image'):
            self.filtered_image = self.original_image.copy()
            self.history = [self.filtered_image.copy()]
            self.history_position = 0
            self.zoom_factor = 1.0
            self.show_image()
    
    def zoom(self, factor):
        """Zoom in/out the image"""
        self.zoom_factor *= factor
        self.show_image()
    
    def fit_to_window(self):
        """Fit image to window size"""
        if hasattr(self, 'original_image'):
            window_width = self.window.winfo_width() - 100
            window_height = self.window.winfo_height() - 100
            
            img_width, img_height = self.original_size
            width_ratio = window_width / img_width
            height_ratio = window_height / img_height
            
            self.zoom_factor = min(width_ratio, height_ratio)
            self.show_image()