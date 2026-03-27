import cv2
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

def extract_dominant_colors(image_bytes: bytes, num_colors: int = 5):
    """
    Optimized color extraction using unified preprocess for speed.
    """
    from preprocess import preprocess_image
    preprocessed = preprocess_image(image_bytes)
    img_rgb = np.array(preprocessed.resized_rgb_256)
    
    if img_rgb.size == 0:
        return []
    
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 
        10,
        1.0
    )
    
    _, _, centers = cv2.kmeans(
        pixels,
        num_colors,
        None,
        criteria,
        5,
        cv2.KMEANS_PP_CENTERS
    )
    
    colors = []
    for r, g, b in centers:
        color_name = _rgb_to_color_name(int(r), int(g), int(b))
        if color_name and color_name not in ['gray', 'neutral']:
            colors.append(color_name)
    
    return colors[:3]

def _rgb_to_color_name(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to color name with improved accuracy.
    Uses HSV color space for better color classification.
    """
    hsv = cv2.cvtColor(
        np.uint8([[[r, g, b]]]), 
        cv2.COLOR_RGB2HSV
    )[0][0]
    
    h, s, v = hsv
    
    if s < 15 or v < 20:
        if v > 200:
            return "white"
        elif v < 50:
            return "black"
        return "gray"
    
    if s < 40:
        if v > 180:
            return "light"
        elif v < 80:
            return "dark"
        return "neutral"
    
    if h < 15 or h > 165:
        if s > 150 and v > 100:
            return "red"
    elif 15 <= h < 35:
        if s > 100:
            return "orange"
        return "yellow"
    elif 35 <= h < 70:
        if s > 100:
            return "green"
    elif 70 <= h < 100:
        return "cyan"
    elif 100 <= h < 130:
        return "blue"
    elif 130 <= h < 165:
        return "purple"
    
    return "colorful"

def extract_colors_simple(image_bytes: bytes) -> list:
    """
    Simple fallback color extraction.
    """
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    if img is None or img.size == 0:
        return []
    
    img = cv2.resize(img, (100, 100))
    avg_color = np.mean(img, axis=(0, 1))
    r, g, b = int(avg_color[2]), int(avg_color[1]), int(avg_color[0])
    
    color = _rgb_to_color_name(r, g, b)
    return [color] if color not in ["gray", "neutral", "colorful"] else []

