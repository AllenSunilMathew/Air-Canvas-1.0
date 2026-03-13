import cv2
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

def extract_dominant_colors(image_bytes: bytes, num_colors: int = 5):
    """
    Enhanced color extraction with better accuracy and performance.
    Uses K-means clustering with optimized parameters.
    """
    # Decode image
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    if img is None or img.size == 0:
        return []
    
    # Resize for faster processing (150x150 is sufficient for color analysis)
    img = cv2.resize(img, (150, 150), interpolation=cv2.INTER_AREA)
    
    # Convert to RGB (OpenCV uses BGR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Reshape to pixel array
    pixels = img_rgb.reshape(-1, 3).astype(np.float32)
    
    # Use K-means++ for better initial centroid selection
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 
        20,  # Increased iterations for better convergence
        1.0
    )
    
    _, _, centers = cv2.kmeans(
        pixels,
        num_colors,
        None,
        criteria,
        10,
        cv2.KMEANS_PP_CENTERS  # Better initialization
    )
    
    # Convert centers to color names
    colors = []
    for r, g, b in centers:
        color_name = _rgb_to_color_name(int(r), int(g), int(b))
        if color_name:
            colors.append(color_name)
    
    # Return most common colors (deduplicated)
    return list(dict.fromkeys(colors))[:3]  # Top 3 unique colors


def _rgb_to_color_name(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to color name with improved accuracy.
    Uses HSV color space for better color classification.
    """
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(
        np.uint8([[[r, g, b]]]), 
        cv2.COLOR_RGB2HSV
    )[0][0]
    
    h, s, v = hsv
    
    # Check for grayscale (low saturation)
    if s < 15 or v < 20:
        if v > 200:
            return "white"
        elif v < 50:
            return "black"
        return "gray"
    
    # Check for low saturation (pastel tones)
    if s < 40:
        if v > 180:
            return "light"
        elif v < 80:
            return "dark"
        return "neutral"
    
    # Determine hue-based colors
    # OpenCV hue range is 0-180 (half of 0-360)
    if h < 15 or h > 165:  # Red (wraps around)
        if s > 150 and v > 100:
            return "red"
    elif 15 <= h < 35:     # Orange/Yellow
        if s > 100:
            return "orange"
        return "yellow"
    elif 35 <= h < 70:     # Green
        if s > 100:
            return "green"
    elif 70 <= h < 100:    # Cyan
        return "cyan"
    elif 100 <= h < 130:   # Blue
        return "blue"
    elif 130 <= h < 165:   # Purple/Magenta
        return "purple"
    
    return "colorful"


def extract_colors_simple(image_bytes: bytes) -> list:
    """
    Simple fallback color extraction using histogram analysis.
    Faster but less accurate than K-means approach.
    """
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    if img is None or img.size == 0:
        return []
    
    # Resize
    img = cv2.resize(img, (100, 100))
    
    # Calculate average color
    avg_color = np.mean(img, axis=(0, 1))
    r, g, b = int(avg_color[2]), int(avg_color[1]), int(avg_color[0])
    
    color = _rgb_to_color_name(r, g, b)
    return [color] if color not in ["gray", "neutral", "colorful"] else []

