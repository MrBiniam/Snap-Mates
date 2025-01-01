import os
import cv2
import numpy as np
from threading import Thread
from queue import Queue
from advanced_filters import AdvancedFilters

class BatchProcessor:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.processing_queue = Queue()
        self.results_queue = Queue()
        self.current_filter = None
        self.filter_params = {}
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def process_image(self, image_path, filter_name, params=None):
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Apply filter
            if hasattr(AdvancedFilters, filter_name):
                filter_func = getattr(AdvancedFilters, filter_name)
                if params:
                    processed = filter_func(image, **params)
                else:
                    processed = filter_func(image)
            else:
                return None
            
            # Convert back to BGR for saving
            processed = cv2.cvtColor(processed, cv2.COLOR_RGB2BGR)
            return processed
            
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")
            return None
    
    def worker(self):
        while True:
            # Get image path from queue
            item = self.processing_queue.get()
            if item is None:
                break
                
            image_path, output_path = item
            
            # Process image
            result = self.process_image(image_path, self.current_filter, self.filter_params)
            
            if result is not None:
                # Save processed image
                cv2.imwrite(output_path, result)
                self.results_queue.put((image_path, True))
            else:
                self.results_queue.put((image_path, False))
            
            self.processing_queue.task_done()
    
    def process_directory(self, filter_name, params=None, num_threads=4):
        self.current_filter = filter_name
        self.filter_params = params or {}
        
        # Start worker threads
        threads = []
        for _ in range(num_threads):
            t = Thread(target=self.worker)
            t.start()
            threads.append(t)
        
        # Add images to queue
        count = 0
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                input_path = os.path.join(self.input_dir, filename)
                output_path = os.path.join(self.output_dir, f"processed_{filename}")
                self.processing_queue.put((input_path, output_path))
                count += 1
        
        # Add None to queue to signal threads to exit
        for _ in range(num_threads):
            self.processing_queue.put(None)
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Collect results
        results = []
        while not self.results_queue.empty():
            results.append(self.results_queue.get())
        
        return results
    
    @staticmethod
    def create_contact_sheet(image_paths, cols=5, thumbnail_size=(200, 200)):
        """Create a contact sheet from multiple images"""
        images = []
        for path in image_paths:
            img = cv2.imread(path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, thumbnail_size)
                images.append(img)
        
        if not images:
            return None
        
        rows = (len(images) + cols - 1) // cols
        cell_width, cell_height = thumbnail_size
        
        # Create blank contact sheet
        contact_sheet = np.zeros((cell_height * rows, cell_width * cols, 3), dtype=np.uint8)
        
        # Place images in grid
        for idx, img in enumerate(images):
            i, j = divmod(idx, cols)
            y = i * cell_height
            x = j * cell_width
            contact_sheet[y:y + cell_height, x:x + cell_width] = img
        
        return contact_sheet 