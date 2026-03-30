import io
import base64
import hashlib
import time
import asyncio
import threading
from queue import Queue, PriorityQueue
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import json
import re
import gc
import warnings
warnings.filterwarnings("ignore")

# Import optimized modules
from preprocess import preprocess_image
from vision_prompt import sketch_to_prompt, clear_cache
from color_analyzer import extract_dominant_colors
from prompt_enhancer import enhance_prompt
from sd15_utils import generate_image, warmup_model, device as sd_device, cleanup as sd_cleanup
from shape_processor import detect_and_straighten_shapes, strokes_to_3d
from ocr import ocr_image

app = FastAPI(title="Sketch-to-Image API (Optimized)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

import collections
from datetime import datetime, timedelta

# ==================== ENHANCED CACHING + THROTTLING ====================
_response_cache = {}
_feature_cache = {}
MAX_CACHE_SIZE = 100
CACHE_TTL = timedelta(minutes=5)

# Semaphore for concurrent SD generations (max 3)
semaphore = asyncio.Semaphore(3)

def _get_image_hash(image_bytes: bytes) -> str:
    

def _get_cache_key(image_bytes: bytes, style: str) -> str:
    async def process_request_async(image_bytes: bytes, style: str) -> dict:

class TTLCache:
    def __init__(self, maxsize=100, ttl=timedelta(minutes=5)):
        \"\"\"Optimized async pipeline with unified preprocess and torch contexts.\"\"\"
        self.maxsize = maxsize
        self.ttl = ttl
    
    def get(self, key):
        cache_key = _get_cache_key(image_bytes, style)
            item = self.cache[key]
            if datetime.now() - item['time'] < self.ttl:
        
                return item['value']
            else:
        # Check cache first
        return None
    
    def set(self, key, value):
        if cache_key in _response_cache:
            self.cache.popitem(last=False)
        self.cache[key] = {'value': value, 'time': datetime.now()}

response_cache = TTLCache(MAX_CACHE_SIZE, CACHE_TTL)

        result = _response_cache[cache_key].copy()
        result[\"cached\"] = True
        return result
    
    print(\"[API] Processing new request (optimized pipeline)...\")

    # Unified preprocess ONCE
    preprocessed = preprocess_image(image_bytes)
    
    import torch
    
    # Parallel BLIP + Colors (non-blocking)
    caption_task = asyncio.to_thread(sketch_to_prompt, image_bytes)
    colors_task = asyncio.to_thread(extract_dominant_colors, image_bytes)
    caption, colors = await asyncio.gather(caption_task, colors_task)
    
    # Enhance prompt
    threed_caption = f\"3D extruded realistic {caption}, volumetric depth, solid object\"
    prompt, negative_prompt = enhance_prompt(threed_caption, colors, style)
    
    # Straighten shapes
    try:
        shapes = detect_and_straighten_shapes(image_bytes)
        straightened_bytes = base64.b64decode(shapes[\"straightened_sketch_b64\"])
        straightened_b64 = shapes[\"straightened_sketch_b64\"]
    except:
        print(\"[API] shape_processor unavailable, using preprocessed sketch\")
        straightened_bytes = preprocessed.to_bytes()
        straightened_b64 = base64.b64encode(straightened_bytes).decode()
    
    depth_b64 = \"\"  # TODO Phase 2
    
    # Generate with inference optimizations
    with torch.inference_mode(), torch.no_grad():
        output_image = generate_image(prompt, negative_prompt, straightened_bytes, style)
    
    # Convert result
    buffer = io.BytesIO()
    output_image.save(buffer, format=\"PNG\", optimize=True)
    buffer.seek(0)
    
    result = {
        \"image\": base64.b64encode(buffer.getvalue()).decode(),
        \"caption\": caption,
        \"threed_caption\": threed_caption,
        \"colors\": colors,
        \"straightened_sketch\": straightened_b64,
        \"depth_map\": depth_b64,
        \"preprocessed\": True,
        \"cached\": False
    }
    
    # Smart cache (LRU-like: evict oldest)
    if len(_response_cache) >= MAX_CACHE_SIZE:
        oldest_key = min(_response_cache, key=_response_cache.get)  # Simple LRU approx
        del _response_cache[oldest_key]
    _response_cache[cache_key] = result
    
    # Aggressive cleanup
    if hasattr(torch, 'cuda'):
        torch.cuda.empty_cache()
    gc.collect()
    
    return result
            _response_cache.pop(next(iter(_response_cache)))
        _response_cache[cache_key] = result
        
        # Force garbage collection
        gc.collect()
        
        return result
async def startup_event():
    print("\n" + "="*60)
    print("🚀 Sketch-to-Image API v2.0 (FULLY OPTIMIZED)")
    print("="*60)
    print(f"� device: {sd_device}")
    
    if sd_device == "cuda":
        try:
            warmup_model()
        except Exception as e:
            print(f"⚠️  Warmup: {e}")
    
    print("✅ Ready!\n" + "="*60 + "\n")

@app.get("/")
def home():
    return {
        "status": "Sketch-to-Image Generator API",
        "version": "2.0 Ultra-Optimized",
        "device": sd_device,
        "optimizations": [
            "UniPCMultistepScheduler",
            "xformers attention",
            "VAE slicing",
            "torch.compile",
            "8-bit BLIP quantization",
            "Multi-level caching",
            "TF32 acceleration",
            "Model CPU offload"
        ]
    }

@app.post("/generate")
async def generate(
    image: UploadFile = File(...),
    style: str = Form("realistic")
):
    \"\"\"Ultra-optimized async generation endpoint.\"\"\"
    start_time = time.perf_counter()
    image_bytes = await image.read()
    
    try:
        result = await process_request_async(image_bytes, style)
        
        elapsed = time.perf_counter() - start_time
        result[\"timing\"] = {
            \"total\": round(elapsed, 3),
            \"preprocessed\": True,
            \"cached\": result.pop(\"cached\", False)
        }
        
        print(f\"⏱️  Optimized: {elapsed:.3f}s\" + (\" (cached)\" if result[\"timing\"][\"cached\"] else \"\"))
        return result
        
    except Exception as e:
        import traceback
        print(f\"❌ Error: {e}\\\\n{traceback.format_exc()}\")
        return {\"error\": str(e)}, 500


@app.post("/generate/progress")
async def generate_with_progress(
    image: UploadFile = File(...),
    style: str = Form("realistic")
):
    """SSE endpoint with progress updates"""
    async def event_stream():
        image_bytes = await image.read()
        
        yield "data: " + json.dumps({"status": "start", "progress": 0}) + "\n\n"
        await asyncio.sleep(0.05)
        
        # Check cache
        cache_key = _get_cache_key(image_bytes, style)
        if cache_key in _response_cache:
            result = _response_cache[cache_key]
            yield "data: " + json.dumps({
                "status": "complete", 
                "progress": 100, 
                "result": result,
                "cached": True
            }) + "\n\n"
            return
        
        yield "data: " + json.dumps({"status": "analyze", "progress": 10}) + "\n\n"
        
        caption = sketch_to_prompt(image_bytes)
        yield "data: " + json.dumps({"status": "caption", "progress": 30, "caption": caption}) + "\n\n"
        
        colors = extract_dominant_colors(image_bytes)
        yield "data: " + json.dumps({"status": "colors", "progress": 40, "colors": colors}) + "\n\n"
        
        prompt, negative_prompt = enhance_prompt(caption, colors, style)
        yield "data: " + json.dumps({"status": "generate", "progress": 50, "message": "Creating image..."}) + "\n\n"
        
        output_image = generate_image(prompt, negative_prompt, image_bytes, style)
        yield "data: " + json.dumps({"status": "complete", "progress": 90}) + "\n\n"
        
        buffer = io.BytesIO()
        output_image.save(buffer, format="PNG")
        buffer.seek(0)
        
        result = {
            "image": base64.b64encode(buffer.getvalue()).decode(),
            "caption": caption,
            "colors": colors
        }
        
        yield "data: " + json.dumps({"status": "done", "progress": 100, "result": result}) + "\n\n"
        
        # Cleanup
        gc.collect()
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/cache/clear")
def clear_all_caches():
    """Clear all caches and free memory"""
    global _response_cache, _feature_cache
    _response_cache = {}
    _feature_cache = {}
    clear_cache()
    sd_cleanup()
    gc.collect()
    return {"status": "All caches cleared, memory freed"}


@app.get("/cache/stats")
def cache_statistics():
    """Show cache statistics"""
    return {
        "response_cache": len(_response_cache),
        "feature_cache": len(_feature_cache),
        "max_cache": MAX_CACHE_SIZE
    }


@app.post("/memory/free")
def free_memory():
    """Free GPU memory"""
    gc.collect()
    sd_cleanup()
    if sd_device == "cuda":
        import torch
        torch.cuda.empty_cache()
    return {"status": "Memory freed"}


@app.get("/health")
def health_check():
    """Health check"""
    info = {"status": "healthy", "device": sd_device}
    if sd_device == "cuda":
        import torch
        info["gpu_memory"] = f"{torch.cuda.memory_allocated()/1e9:.1f}GB / {torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB"
    return info


# Add async ping for keeping connection alive
@app.post("/to3d")
async def to3d(strokes: str = Form(...)):
    """Air canvas strokes → 3D GLTF model"""
    from shape_processor import strokes_to_3d
    result = strokes_to_3d(strokes)
    return result

@app.post("/preview_inflate")
async def preview_inflate(image: UploadFile = File(...)):
    """Preview 3D inflate (depth map) after straightening - fast response"""
    image_bytes = await image.read()
    maps = inflate_shapes(image_bytes)
    return {
        "depth_b64": maps["depth_b64"],
        "straightened_sketch_b64": maps["straightened_sketch_b64"]
    }

@app.get("/ping")\n    def ping():\n        return "OK"\n\n\n@app.post("/ocr")\nasync def ocr_handwriting(image_b64: str = Form(...)):\n    \"\"\"OCR air handwriting to clean text\"\"\"\n    return ocr_image(image_b64)


    
