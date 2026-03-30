import torch, cv2, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from diffusers import (
    StableDiffusionControlNetPipeline, 
    ControlNetModel, 
    UniPCMultistepScheduler,
    AutoencoderKL
)
import warnings
warnings.filterwarnings("ignore")

# Device configuration with advanced settings
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[SD] Using device: {device}")

# Enable TF32 on Ampere GPUs for faster computation
if torch.cuda.is_available():
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.benchmark = True  # Enable cudnn benchmarking
    print("[SD] TF32 enabled for faster computation")

# ControlNet model with optimized settings
controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_scribble",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    use_safetensors=True  # Faster loading
)

# Load custom VAE for better quality
try:
    vae = AutoencoderKL.from_pretrained(
        "stabilityai/sd-vae-ft-mse",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    )
    print("[SD] Custom VAE loaded")
except:
    vae = None
    print("[SD] Using default VAE")

# Stable Diffusion pipeline with ALL optimizations
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "SG161222/Realistic_Vision_V5.1_noVAE",
    controlnet=controlnet,
    vae=vae,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    safety_checker=None,
    use_safetensors=True
).to(device)

# ==================== PERFORMANCE OPTIMIZATIONS ====================

# 1. Use fastest scheduler - UniPC (2-3x faster than DPM++)
pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
print("[SD] ✓ UniPCMultistepScheduler - fastest scheduler")

# 2. Enable xformers (2-3x faster on supported GPUs)
try:
    pipe.enable_xformers_memory_efficient_attention()
    print("[SD] ✓ xformers memory-efficient attention")
except ImportError:
    print("[SD] ✗ xformers not available")

# 3. Enable attention slicing (reduces memory by 50%)
pipe.enable_attention_slicing("auto")
print("[SD] ✓ Attention slicing enabled")

# 4. Enable VAE slicing (for lower memory)
pipe.enable_vae_slicing()
print("[SD] ✓ VAE slicing enabled")

# 5. CPU offloading for systems with limited VRAM
# Only enable if GPU memory is limited (< 6GB)
if device == "cuda":
    gpu_mem = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    if gpu_mem < 6:
        pipe.enable_sequential_cpu_offload()
        print(f"[SD] ✓ CPU offloading enabled ({gpu_mem:.1f}GB GPU)")
    else:
        # 6. Model offloading for better memory management
        pipe.enable_model_cpu_offload()
        print("[SD] ✓ Model CPU offload enabled")

# 7. torch.compile with fallback + FP8 check
if hasattr(torch.nn.functional, 'scaled_dot_product_attention') and torch.__version__ >= '2.1':
    
        pipe.enable_flash_attention_2()
        print("[SD] ✓ Flash Attention 2 (FP8 capable)")
    except:
        pass

try:
    pipe.unet = torch.compile(pipe.unet, mode="reduce-overhead")
    pipe.vae = torch.compile(pipe.vae, mode="reduce-overhead")
    print("[SD] ✓ torch.compile (UNET + VAE)")
except Exception as e:
    try:
        pipe = torch.compile(pipe, mode="default")
        print("[SD] ✓ torch.compile (full pipeline fallback)")
    except Exception as e2:
        print(f"[SD] - torch.compile skipped: {e2}")

# 8. Set optimal performance defaults
pipe.set_progress_bar_config(disable=True)  # Disable progress bar for speed
torch.cuda.empty_cache()  # Clear cache before use

# ==================== PREPROCESSING ====================

def preprocess_sketch(image_bytes: bytes) -> Image.Image:
    """Enhanced sketch preprocessing with multiple optimizations"""
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)

    if img is None or img.size == 0:
        return Image.new("RGB", (512, 512), "white")

    # Fast resize using INTER_AREA
    img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)
    
    # Denoise using fast Gaussian blur
    img = cv2.fastGaussBlur(img, (3, 3), 0)
    
    # Adaptive thresholding with Otsu's method
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Morphological operations - optimized kernels
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    
    # Convert to RGB
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    
    return Image.fromarray(edges)

def sharpen(img):
    """Enhanced sharpening pipeline"""
    # Unsharp mask
    sharpened = img.filter(ImageFilter.UnsharpMask(
        radius=1.5, percent=120, threshold=3
    ))
    
    # Contrast enhancement
    enhancer = ImageEnhance.Contrast(sharpened)
    sharpened = enhancer.enhance(1.1)
    
    # Slight sharpness boost
    sharpness = ImageEnhance.Sharpness(sharpened)
    sharpened = sharpness.enhance(1.05)
    
    return sharpened

# Optimized generation parameters
STYLE_PARAMS = {
    "realistic": {"cfg": 7.0, "steps": 20, "control_scale": 0.9},
    "animated": {"cfg": 8.0, "steps": 15, "control_scale": 1.2},
    "outline": {"cfg": 8.5, "steps": 15, "control_scale": 1.0}
}

def generate_image(prompt, negative_prompt, image_bytes, style):
    \"\"\"Generate with preprocess integration & dynamic denoising.\"\"\"
    from preprocess import preprocess_image
    preprocessed = preprocess_image(image_bytes)
    control_image = preprocessed.controlnet_sketch
    params = STYLE_PARAMS.get(style, STYLE_PARAMS["realistic"])
    
    # Dynamic denoising + steps based on image complexity (edge density)
    gray = np.array(control_image.convert('L'))
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.mean(edges > 0) / 255
    
    # Dynamic steps: simpler sketches fewer steps (faster)
    dynamic_steps = max(15, min(25, int(20 + edge_density * 10)))
    params["steps"] = dynamic_steps
    
    denoising_strength = max(0.75, min(0.95, 0.85 + edge_density * 0.1))
    print(f"[SD] Dynamic: {dynamic_steps} steps, density={edge_density:.2f}, strength={denoising_strength:.2f}")

    
    # Clear GPU cache before generation
    if device == "cuda":
        torch.cuda.empty_cache()
    
    # Generate with optimized settings
    with torch.inference_mode():
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=control_image,
            guidance_scale=params["cfg"],
            controlnet_conditioning_scale=params["control_scale"],
            num_inference_steps=params["steps"],
            width=512,
            height=512,
            strength=denoising_strength,
            denoising_end=0.95,
        )
    
    return sharpen(result.images[0])

# Warmup function
def warmup_model():
    """Multi-step warmup for optimal performance"""
    print("[SD] Warming up model...")
    
    # Step 1: Small warmup
    dummy = Image.new("RGB", (512, 512), "white")
    _ = pipe(
        prompt="warmup",
        negative_prompt="",
        image=dummy,
        guidance_scale=7.0,
        num_inference_steps=1
    )
    
    # Step 2: Full warmup
    _ = pipe(
        prompt="test",
        negative_prompt="",
        image=dummy,
        guidance_scale=7.0,
        num_inference_steps=2
    )
    
    # Clear cache after warmup
    if device == "cuda":
        torch.cuda.empty_cache()
    
    print("[SD] ✓ Warmup complete!")

def cleanup():
    """Cleanup GPU memory"""
    if device == "cuda":
        torch.cuda.empty_cache()
    print("[SD] Memory cleaned up")

