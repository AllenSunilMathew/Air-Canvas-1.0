import pytesseract
from PIL import Image
import io
import base64
import re

# Windows Tesseract path (auto-detect/install)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def ocr_image(image_b64: str) -> dict:
    """
    OCR handwriting from base64 image.
    Returns: {'text': 'recognized text', 'confidence': float}
    """
    try:
        # Decode base64
        image_data = base64.b64decode(image_b64)
        img = Image.open(io.BytesIO(image_data))
        
        # Preprocess for handwriting: grayscale, threshold
        img = img.convert('L')  # Grayscale
        img = img.point(lambda p: p > 128 and 255)  # Binary threshold
        
        # OCR config for handwriting/single line
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?-'
        
        text = pytesseract.image_to_string(img, config=custom_config).strip()
        
        # Clean text (remove empty lines, extra spaces)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        clean_text = ' '.join(lines)
        
        confidence = len(clean_text) / max(len(text), 1)  # Simple metric
        
        return {
            'text': clean_text,
            'raw_text': text,
            'confidence': float(confidence),
            'success': bool(clean_text)
        }
    except Exception as e:
        return {'text': '', 'error': str(e), 'success': False}

def is_text_like(strokes_count: int) -> bool:
    """Heuristic: trigger OCR if 3+ short strokes (letters)"""
    return strokes_count >= 3
