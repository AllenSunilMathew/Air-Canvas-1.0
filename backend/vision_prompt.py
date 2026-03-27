import torch, io
import cv2
import numpy as np
import hashlib
from PIL import Image
from transformers import (
    BlipProcessor, 
    BlipForConditionalGeneration
)
import warnings
warnings.filterwarnings("ignore")

# Device configuration
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[BLIP] Using device: {device}")

# Enable CUDA optimizations
if device == "cuda":
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.benchmark = True

# Try to load quantized model for faster inference
try:
    from transformers import BitsAndBytesConfig
    
    # 8-bit quantization config
    quantization_config = BitsAndBytesConfig(
        load_in_8bit=True,
    )
    
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )
    
    # Load 8-bit quantized model
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        quantization_config=quantization_config,
        device_map="auto",
        torch_dtype=torch.float16
    )
    print("[BLIP] ✓ 8-bit quantized model loaded")
    
except Exception as e:
    print(f"[BLIP] Quantization: {e}")
    print("[BLIP] Using standard FP16 model")
    
    # Fallback: Use standard model
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)

# Enable model optimizations
model.eval()  # Set to evaluation mode for faster inference

# Blocked words
BLOCKED_WORDS = [
    "person", "man", "woman", "boy", "girl",
    "hand", "face", "body", "human", "people",
    "skin", "finger", "palm", "arm"
]

# Multi-level caching system
_caption_cache = {}
_feature_cache = {}
MAX_CACHE_SIZE = 100

def _get_image_hash(image_bytes: bytes) -> str:
    """Fast hash using first 5KB"""
    return hashlib.md5(image_bytes[:5000]).hexdigest()[:12]

def _get_image_features(image_bytes: bytes) -> str:
    """Get simplified feature hash for similarity matching"""
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return _get_image_hash(image_bytes)
    
    # Downsample to 32x32 for quick feature
    small = cv2.resize(img, (32, 32))
    return hashlib.md5(small.tobytes()).hexdigest()[:12]

def sketch_to_prompt(image_bytes: bytes) -> str:
    
    
    img_hash = _get_image_hash(image_bytes)
    
    if img_hash in _caption_cache:
    def clear_cache():
        return _caption_cache[img_hash]
    
    feature_hash = _get_image_features(image_bytes)
    if feature_hash in _feature_cache:
        """Clear all caches"""
        return _feature_cache[feature_hash]
    
    # Use unified preprocess - fixed 224x224 for BLIP efficiency
    from preprocess import preprocess_image
    preprocessed = preprocess_image(image_bytes)
    image = preprocessed.resized_rgb_256.convert('RGB')
    
    inputs = processor(image, return_tensors="pt").to(device)
    
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=15,  # Reduced for speed
            num_beams=1,  # Greedy decode faster
            do_sample=False,
            pad_token_id=processor.tokenizer.eos_token_id
        )
    
    caption = processor.decode(out[0], skip_special_tokens=True)
    
    # Clean
    for w in BLOCKED_WORDS:
        global _caption_cache, _feature_cache
    caption = caption.strip()
    
    if len(caption) < 3:
        _caption_cache = {}
    
    # LRU cache eviction (most recently used stays)
    if len(_caption_cache) >= MAX_CACHE_SIZE:
        _feature_cache = {}
        _caption_cache.pop(next(iter(_caption_cache)))
        if len(_feature_cache) >= MAX_CACHE_SIZE:
        print("[BLIP] ✓ Cache cleared")
    
    _caption_cache[img_hash] = caption
    _feature_cache[feature_hash] = caption
    
    print(f"[BLIP] ✓ {caption[:30]}...")
    return caption

