
import cv2
import numpy as np

def extract_dominant_colors(image_bytes: bytes):
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None or img.size == 0:
        return []

    img = cv2.resize(img, (150, 150))
    pixels = img.reshape(-1, 3).astype(np.float32)

    _, _, centers = cv2.kmeans(
        pixels,
        3,
        None,
        (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0),
        10,
        cv2.KMEANS_RANDOM_CENTERS
    )

    colors = []
    for b, g, r in centers:
        if r > g and r > b:
            colors.append("red")
        elif g > r and g > b:
            colors.append("green")
        elif b > r and b > g:
            colors.append("blue")
        else:
            colors.append("neutral")

    return list(set(colors))