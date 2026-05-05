import cv2
import numpy as np
from loguru import logger

class ImageProcessor:
    @staticmethod
    def preprocess(image_path: str) -> np.ndarray:
        """Clean and prepare chart image for analysis"""
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Resize if too large
        height, width = img.shape[:2]
        if width > 1920:
            scale = 1920 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Enhance contrast
        enhanced = cv2.equalizeHist(denoised)
        
        logger.info(f"Image preprocessed: {image_path}")
        
        return enhanced
