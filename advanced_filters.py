import cv2
import numpy as np

class AdvancedFilters:
    @staticmethod
    def sepia(image):
        sepia_matrix = np.array([
            [0.393, 0.769, 0.189],
            [0.349, 0.686, 0.168],
            [0.272, 0.534, 0.131]
        ])
        sepia_image = cv2.transform(image, sepia_matrix)
        sepia_image[np.where(sepia_image > 255)] = 255
        return sepia_image.astype(np.uint8)
    
    @staticmethod
    def vintage(image):
        # Add warm temperature
        image = cv2.convertScaleAbs(image, alpha=1.3, beta=20)
        # Add slight blue tint to shadows
        b, g, r = cv2.split(image)
        b = cv2.convertScaleAbs(b, alpha=1.1, beta=10)
        return cv2.merge([b, g, r])
    
    @staticmethod
    def vignette(image, intensity=0.5):
        rows, cols = image.shape[:2]
        # Generate vignette mask
        kernel_x = cv2.getGaussianKernel(cols, cols/2)
        kernel_y = cv2.getGaussianKernel(rows, rows/2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        mask = 1 - (1 - mask) * intensity
        
        # Apply the mask to each channel
        result = image.copy()
        for i in range(3):
            result[:, :, i] = result[:, :, i] * mask
        
        return result.astype(np.uint8)
    
    @staticmethod
    def adjust_temperature(image, value=30):
        # Split the channels
        b, g, r = cv2.split(image)
        
        if value > 0:  # Warmer
            r = cv2.add(r, value)
            b = cv2.subtract(b, value)
        else:  # Cooler
            r = cv2.subtract(r, abs(value))
            b = cv2.add(b, abs(value))
            
        return cv2.merge([b, g, r])
    
    @staticmethod
    def adjust_saturation(image, value=1.5):
        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s, value)
        s = np.clip(s, 0, 255)
        hsv = cv2.merge([h, s, v])
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    @staticmethod
    def analyze_image(image):
        # Calculate histogram
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        
        # Calculate basic statistics
        mean = np.mean(image)
        std = np.std(image)
        
        # Edge detection for detail analysis
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.count_nonzero(edges) / (edges.shape[0] * edges.shape[1])
        
        return {
            'histogram': hist,
            'mean_brightness': mean,
            'std_dev': std,
            'edge_density': edge_density
        }
    
    @staticmethod
    def denoise(image, strength=10):
        return cv2.fastNlMeansDenoisingColored(image, None, strength, strength, 7, 21)
    
    @staticmethod
    def hdr_effect(image):
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        
        # Merge channels
        lab = cv2.merge([l, a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    
    @staticmethod
    def tilt_shift(image, blur_amount=30):
        h, w = image.shape[:2]
        
        # Create gradient mask
        mask = np.zeros((h, w), dtype=np.float32)
        center_y = h // 2
        gradient_size = h // 3
        
        mask[center_y-gradient_size:center_y+gradient_size, :] = \
            np.tile(np.linspace(0, 1, gradient_size*2), (w, 1)).T
        
        # Blur the image
        blurred = cv2.GaussianBlur(image, (blur_amount*2+1, blur_amount*2+1), 0)
        
        # Combine original and blurred image using the mask
        mask = np.dstack([mask]*3)
        return (image * mask + blurred * (1 - mask)).astype(np.uint8) 