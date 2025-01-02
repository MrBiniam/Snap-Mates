import cv2
import numpy as np

class AdvancedFilters:
    def __init__(self):
        pass

    def unsharp_mask(self, image):
        """Apply unsharp mask filter"""
        if image is None:
            raise ValueError("Invalid image input")
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)
        
        gaussian = cv2.GaussianBlur(image, (9, 9), 10.0)
        unsharp_image = cv2.addWeighted(image, 1.5, gaussian, -0.5, 0)
        return np.clip(unsharp_image, 0, 255).astype(np.uint8)

    def histogram_equalization(self, image):
        """Apply histogram equalization"""
        if image is None:
            raise ValueError("Invalid image input")
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)

        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)

        # Merge channels
        lab = cv2.merge((l, a, b))

        # Convert back to RGB
        result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        return np.clip(result, 0, 255).astype(np.uint8)

    def sepia(self, image):
        """Apply sepia filter"""
        if image is None:
            raise ValueError("Invalid image input")
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)

        sepia_filter = np.array([[0.393, 0.769, 0.189],
                                [0.349, 0.686, 0.168],
                                [0.272, 0.534, 0.131]])
        sepia_img = cv2.transform(image, sepia_filter)
        sepia_img = np.clip(sepia_img, 0, 255)
        return sepia_img.astype(np.uint8)

    def vintage(self, image):
        """Apply vintage filter"""
        if image is None:
            raise ValueError("Invalid image input")
        if image.dtype != np.uint8:
            image = np.clip(image, 0, 255).astype(np.uint8)

        rows, cols = image.shape[:2]

        # Create a warm color overlay
        overlay = np.full_like(image, (255, 240, 220))  # Warm color
        vintage = cv2.addWeighted(image, 0.8, overlay, 0.2, 0)

        # Add vignette effect
        kernel_x = cv2.getGaussianKernel(cols, cols / 2)
        kernel_y = cv2.getGaussianKernel(rows, rows / 2)
        kernel = kernel_y * kernel_x.T
        mask = kernel / kernel.max()
        mask = mask ** 0.5  # Adjust vignette strength

        # Apply vignette
        vintage = vintage * mask[:, :, np.newaxis]

        # Add slight blur for dreamy effect
        vintage = cv2.GaussianBlur(vintage, (3, 3), 0)

        return np.clip(vintage, 0, 255).astype(np.uint8)
