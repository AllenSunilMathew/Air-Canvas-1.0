
import torch, cv2, numpy as np
from PIL import Image, ImageFilter
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

device = "cuda" if torch.cuda.is_available() else "cpu"

controlnet = ControlNetModel.from_pretrained(
    "lllyasviel/control_v11p_sd15_scribble",
    torch_dtype=torch.float16
)

pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "SG161222/Realistic_Vision_V5.1_noVAE",
    controlnet=controlnet,
    torch_dtype=torch.float16,
    safety_checker=None
).to(device)

pipe.enable_attention_slicing()

def preprocess_sketch(image_bytes: bytes) -> Image.Image:
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_GRAYSCALE)

    if img is None or img.size == 0:
        return Image.new("RGB", (512, 512), "white")

    edges = cv2.Canny(img, 50, 150)
    edges = cv2.dilate(edges, np.ones((4, 4), np.uint8), 2)
    edges = cv2.resize(edges, (512, 512))
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

    return Image.fromarray(edges)

def sharpen(img):
    return img.filter(ImageFilter.UnsharpMask(
        radius=1.5, percent=120, threshold=3
    ))

def generate_image(prompt, negative_prompt, image_bytes, style):
    control_image = preprocess_sketch(image_bytes)

    if style == "realistic":
        cfg = 7.0  # Slightly lower for natural, less artifact-prone realism
        steps = 50  # Increased for finer details in realistic scenes
        control_scale = 0.9  # Balanced to preserve sketch while enhancing realism
    elif style == "animated":
        cfg = 8.0  # Higher for vibrant, stylized animation
        steps = 35  # Sufficient for animated style without over-processing
        control_scale = 1.2  # Stronger control to maintain cartoonish fidelity
    else:  # Default (e.g., artistic or general)
        cfg = 8.5  # Balanced for creative freedom
        steps = 40  # Good compromise for detail and speed
        control_scale = 1.0  # Moderate control for flexible

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=control_image,
        guidance_scale=cfg,
        controlnet_conditioning_scale=control_scale,
        num_inference_steps=steps
    )

    return sharpen(result.images[0])
