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
import os

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
    
    def set_filter_params(self, params):
        """Update filter parameters and trigger update if needed"""
        try:
            # Store old parameters for comparison
            old_params = self.filter_params.copy()
            
            # Update parameters
            self.filter_params.update(params)
            
            # Check if any parameter actually changed
            changed = False
            for key, value in params.items():
                if key in old_params and old_params[key] != value:
                    changed = True
                    print(f"Parameter {key} changed from {old_params[key]} to {value}")
                    break
            
            # Only update if parameters changed
            if changed:
                self.update()
                
        except Exception as e:
            print(f"Error updating filter parameters: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def apply_filter(self, image):
        """Apply selected filters to the image"""
        try:
            result = image.copy()
            
            # Basic filters
            if self.all_filters['gray']:
                result = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            
            if self.all_filters['threshold']:
                gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
                _, result = cv2.threshold(gray, self.filter_params['threshold'], 255, cv2.THRESH_BINARY)
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            
            # Enhancement filters
            if self.all_filters['increaseContrast']:
                result = cv2.convertScaleAbs(result, alpha=1.5, beta=0)
            
            if self.all_filters['decreaseContrast']:
                result = cv2.convertScaleAbs(result, alpha=0.5, beta=0)
            
            if self.all_filters['logTransformation']:
                # Convert to float32 for logarithmic operation
                log_img = result.astype(np.float32) / 255.0
                # Add small constant to avoid log(0)
                log_img = np.log(log_img + 1.0)
                # Normalize to 0-255 range
                result = np.uint8(255 * (log_img / np.max(log_img)))
            
            # Color adjustments
            if self.all_filters['temperature']:
                temp = self.filter_params['temperature']
                if temp > 0:  # Warmer
                    result = result.astype(np.float32)
                    result[:,:,2] = np.clip(result[:,:,2] * (1 + temp/100), 0, 255)  # More red
                    result[:,:,0] = np.clip(result[:,:,0] * (1 - temp/200), 0, 255)  # Less blue
                    result = result.astype(np.uint8)
                else:  # Cooler
                    result = result.astype(np.float32)
                    result[:,:,0] = np.clip(result[:,:,0] * (1 - temp/100), 0, 255)  # More blue
                    result[:,:,2] = np.clip(result[:,:,2] * (1 + temp/200), 0, 255)  # Less red
                    result = result.astype(np.uint8)
            
            if self.all_filters['saturation']:
                # Convert to HSV for saturation adjustment
                hsv = cv2.cvtColor(result, cv2.COLOR_RGB2HSV).astype(np.float32)
                hsv[:,:,1] = np.clip(hsv[:,:,1] * self.filter_params['saturation'], 0, 255)
                result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # Blur filters
            if self.all_filters['gauss']:
                # Ensure kernel size is odd
                kernel_size = int(self.filter_params['blur_radius']) * 2 + 1
                result = cv2.GaussianBlur(result, (kernel_size, kernel_size), 0)
            
            if self.all_filters['median']:
                # Ensure kernel size is odd
                kernel_size = int(self.filter_params['blur_radius']) * 2 + 1
                result = cv2.medianBlur(result, kernel_size)
            
            if self.all_filters['average']:
                kernel_size = int(self.filter_params['blur_radius']) * 2 + 1
                kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
                result = cv2.filter2D(result, -1, kernel)
            
            # Edge detection
            if self.all_filters['sobel']:
                gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
                sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                # Compute magnitude and normalize
                magnitude = np.sqrt(sobelx**2 + sobely**2)
                result = np.uint8(255 * magnitude / np.max(magnitude))
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            
            if self.all_filters['laplace']:
                gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                # Normalize the result
                result = np.uint8(255 * np.abs(laplacian) / np.max(np.abs(laplacian)))
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            
            if self.all_filters['prewitt']:
                gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
                kernelx = np.array([[1,1,1],[0,0,0],[-1,-1,-1]])
                kernely = np.array([[-1,0,1],[-1,0,1],[-1,0,1]])
                prewittx = cv2.filter2D(gray, -1, kernelx)
                prewitty = cv2.filter2D(gray, -1, kernely)
                # Compute magnitude and normalize
                magnitude = np.sqrt(prewittx.astype(float)**2 + prewitty.astype(float)**2)
                result = np.uint8(255 * magnitude / np.max(magnitude))
                result = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            
            # Effects
            if self.all_filters['vignette']:
                rows, cols = result.shape[:2]
                # Generate vignette mask
                kernel_x = cv2.getGaussianKernel(cols, cols/2)
                kernel_y = cv2.getGaussianKernel(rows, rows/2)
                kernel = kernel_y * kernel_x.T
                mask = kernel / kernel.max()
                # Apply vignette strength
                mask = mask ** (2 * self.filter_params['vignette'])
                # Convert to 3 channels and apply
                mask_3d = np.dstack([mask] * 3)
                result = np.uint8(result * mask_3d)
            
            # Advanced filters
            if self.all_filters['unsharp']:
                result = self.advanced_filters.unsharp_mask(result)
            
            if self.all_filters['histogramEqualization']:
                result = self.advanced_filters.histogram_equalization(result)
            
            if self.all_filters['sepia']:
                result = self.advanced_filters.sepia(result)
            
            if self.all_filters['vintage']:
                result = self.advanced_filters.vintage(result)
            
            return result
            
        except Exception as e:
            print(f"Error applying filter: {str(e)}")
            import traceback
            traceback.print_exc()
            return image.copy()

    def update(self):
        """Update the displayed image with current filters"""
        if not hasattr(self, 'original_image'):
            return
            
        try:
            # Start with original image
            self.filtered_image = self.original_image.copy()
            
            # Apply active filters
            if any(self.all_filters.values()):
                self.filtered_image = self.apply_filter(self.filtered_image)
            
            # Add to history if image changed
            if self.history_position < 0 or not np.array_equal(self.filtered_image, self.history[self.history_position]):
                # Truncate history if we're not at the end
                if self.history_position < len(self.history) - 1:
                    self.history = self.history[:self.history_position + 1]
                
                # Add new state to history
                self.history.append(self.filtered_image.copy())
                self.history_position = len(self.history) - 1
                
                print(f"Added to history. Position: {self.history_position}, Total states: {len(self.history)}")
            
            # Update display
            self.show_image()
            
        except Exception as e:
            print(f"Error in update: {str(e)}")
            import traceback
            traceback.print_exc()
            # Revert to original image if error occurs
            self.filtered_image = self.original_image.copy()
            self.show_image()
    
    def create_scrollable_frame(self, parent, row, column):
        """Create a frame with scrollbars"""
        # Create a canvas with scrollbars
        canvas = tk.Canvas(parent, borderwidth=0, highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
        
        # Create the scrollable frame inside the canvas
        scrollable_frame = ttk.Frame(canvas)
        
        # Configure scrolling
        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Update canvas size to match frame if smaller
            frame_width = scrollable_frame.winfo_reqwidth()
            frame_height = scrollable_frame.winfo_reqheight()
            if canvas.winfo_width() < frame_width:
                canvas.configure(width=frame_width)
            if canvas.winfo_height() < frame_height:
                canvas.configure(height=frame_height)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        
        # Add the frame to the canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Update canvas window size when canvas is resized
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Configure scrollbars
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
            if canvas.winfo_height() < scrollable_frame.winfo_reqheight():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Bind shift + mouse wheel to horizontal scroll
        def _on_shift_mousewheel(event):
            if canvas.winfo_width() < scrollable_frame.winfo_reqwidth():
                canvas.xview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)
        
        return scrollable_frame
    
    def show_image(self):
        """Display both original and filtered images side by side with scrollbars"""
        if not hasattr(self, 'original_image') or not hasattr(self, 'filtered_image'):
            print("No images to display")
            return
            
        try:
            # Find the display frames first
            display_frame = None
            original_frame = None
            filtered_frame = None
            
            # Find display frame
            for child in self.window.winfo_children():
                if isinstance(child, ttk.Frame) and str(child).endswith('display_frame'):
                    display_frame = child
                    break
            
            if not display_frame:
                print("Could not find display frame")
                return
                
            # Find image frames
            for child in display_frame.winfo_children():
                if isinstance(child, ttk.LabelFrame):
                    if "Original Image" in str(child.cget("text")):
                        original_frame = child
                    elif "Filtered Image" in str(child.cget("text")):
                        filtered_frame = child
            
            if not original_frame or not filtered_frame:
                print("Could not find image frames")
                return
                
            # Calculate display size while maintaining aspect ratio
            window_width = self.window.winfo_width() - 400  # Account for sidebar and padding
            window_height = self.window.winfo_height() - 300  # Account for top elements and padding
            
            # Calculate scaling factor to fit window while maintaining aspect ratio
            width_ratio = window_width / (2 * self.original_size[0])  # Divide by 2 for side-by-side display
            height_ratio = window_height / self.original_size[1]
            scale_factor = min(width_ratio, height_ratio, self.zoom_factor)
            
            display_size = (int(self.original_size[0] * scale_factor),
                           int(self.original_size[1] * scale_factor))
            
            # Process original image
            original_pil = PIL.Image.fromarray(self.original_image)
            original_pil = original_pil.resize(display_size, PIL.Image.LANCZOS)
            self.original_photo = PIL.ImageTk.PhotoImage(image=original_pil)
            
            # Process filtered image
            filtered_pil = PIL.Image.fromarray(self.filtered_image)
            filtered_pil = filtered_pil.resize(display_size, PIL.Image.LANCZOS)
            self.filtered_photo = PIL.ImageTk.PhotoImage(image=filtered_pil)
            
            # Clear existing content
            for frame in [original_frame, filtered_frame]:
                for widget in frame.winfo_children():
                    widget.destroy()
            
            # Create simple labels for images
            original_label = ttk.Label(original_frame, image=self.original_photo)
            original_label.image = self.original_photo  # Keep a reference
            original_label.pack(expand=True, fill="both", padx=5, pady=5)
            
            filtered_label = ttk.Label(filtered_frame, image=self.filtered_photo)
            filtered_label.image = self.filtered_photo  # Keep a reference
            filtered_label.pack(expand=True, fill="both", padx=5, pady=5)
            
            # Store the labels
            self.original_label = original_label
            self.filtered_label = filtered_label
            
            # Configure minimum size for frames
            min_size = max(display_size[0], display_size[1])
            original_frame.configure(width=min_size, height=min_size)
            filtered_frame.configure(width=min_size, height=min_size)
            
            print("Images displayed successfully")
                
        except Exception as e:
            print(f"Error displaying image: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def select_file(self):
        """Open file dialog to select an image"""
        try:
            img_path = tkinter.filedialog.askopenfilename(
                filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if len(img_path) > 0:
                print(f"Selected image: {img_path}")
                
                # Store the filename
                self.filename = img_path
                
                # Load and convert image
                print("Loading image...")
                self.original_image = cv2.imread(img_path)
                if self.original_image is None:
                    raise ValueError(f"Could not load image from path: {img_path}")
                    
                print(f"Image shape: {self.original_image.shape}")
                
                # Convert BGR to RGB
                self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
                self.filtered_image = self.original_image.copy()
                
                # Store original size and set initial zoom
                self.original_size = (self.original_image.shape[1], self.original_image.shape[0])
                self.zoom_factor = 1.0
                
                print(f"Original size: {self.original_size}")
                
                # Initialize history
                self.history = [self.original_image.copy()]
                self.history_position = 0
                
                # Initialize filter parameters if not already set
                if not hasattr(self, 'filter_params'):
                    self.filter_params = {
                        'intensity': 1.0,
                        'threshold': 127,
                        'temperature': 0,
                        'saturation': 1.0,
                        'vignette': 0.5,
                        'blur_radius': 5
                    }
                
                print("Displaying image...")
                # Show initial image
                self.show_image()
                
                # Update window title with filename
                if hasattr(self.window, 'title'):
                    filename = os.path.basename(img_path)
                    self.window.title(f"GREAT MATES - Computer Science - {filename}")
                    
                print("Image loaded and displayed successfully")
                    
        except Exception as e:
            print(f"Error loading image: {str(e)}")
            import traceback
            traceback.print_exc()
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