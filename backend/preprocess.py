import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import io

class PreprocessedImage:
    """Unified preprocessed image container to avoid redundant operations."""
    def __init__(self, image_bytes: bytes):
        self.original_bytes = image_bytes
        self._rgb_img = None
        self._gray_img = None
        self._resized_rgb_512 = None
        self._resized_rgb_256 = None
        self._resized_gray_512 = None
        self._edge_sketch = None
        self._normalized = None
        
    @property
    def rgb_original(self) -> Image.Image:
        if self._rgb_img is None:
            np_img = np.frombuffer(self.original_bytes, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            if img is not None:
                self._rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                self._rgb_img = Image.fromarray(self._rgb_img)
        return self._rgb_img
    
    @property
    def gray_original(self) -> np.ndarray:
        if self._gray_img is None:
            np_img = np.frombuffer(self.original_bytes, np.uint8)
            self._gray_img = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)
        return self._gray_img
    
    @property
    def resized_rgb_512(self) -> Image.Image:
        if self._resized_rgb_512 is None:
            img = self.rgb_original
            self._resized_rgb_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        return self._resized_rgb_512
    
    @property
    def resized_rgb_256(self) -> Image.Image:
        if self._resized_rgb_256 is None:
            img = self.rgb_original
            self._resized_rgb_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        return self._resized_rgb_256
    
    @property
    def resized_gray_512(self) -> np.ndarray:
        if self._resized_gray_512 is None:
            gray = self.gray_original
            if gray is not None:
                self._resized_gray_512 = cv2.resize(gray, (512, 512), interpolation=cv2.INTER_AREA)
        return self._resized_gray_512
    
    @property
    def controlnet_sketch(self) -> Image.Image:
        if self._edge_sketch is None:
            gray_512 = self.resized_gray_512
            if gray_512 is None:
                self._edge_sketch = Image.new('RGB', (512, 512), (255, 255, 255))
            else:
                # Optimized sketch preprocess: denoise + Otsu + morphology
                denoised = cv2.GaussianBlur(gray_512, (3, 3), 0)
                _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
                cleaned_rgb = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2RGB)
                self._edge_sketch = Image.fromarray(cleaned_rgb)
        return self._edge_sketch
    
    def to_bytes(self, format: str = 'PNG') -> bytes:
        buffer = io.BytesIO()
        self.resized_rgb_512.save(buffer, format=format)
        return buffer.getvalue()

def preprocess_image(image_bytes: bytes) -> PreprocessedImage:
    """Factory: create unified preprocessed image."""
    return PreprocessedImage(image_bytes)

# For backward compatibility
def preprocess_sketch(image_bytes: bytes) -> Image.Image:
    return preprocess_image(image_bytes).controlnet_sketch

