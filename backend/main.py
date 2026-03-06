
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import io, base64

from vision_prompt import sketch_to_prompt
from color_analyzer import extract_dominant_colors
from prompt_enhancer import enhance_prompt
from sd15_utils import generate_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Image-to-Image Style Generator running"}

@app.post("/generate")
async def generate(
    image: UploadFile = File(...),
    style: str = Form("realistic")
):
    image_bytes = await image.read()

    caption = sketch_to_prompt(image_bytes)
    colors = extract_dominant_colors(image_bytes)

    prompt, negative_prompt = enhance_prompt(
        caption=caption,
        colors=colors,
        style=style
    )

    print("STYLE:", style)
    print("PROMPT:", prompt)

    '''output_image = generate_image(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image_bytes=image_bytes
    )
'''
    output_image = generate_image(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image_bytes=image_bytes,
    style=style
)

    buffer = io.BytesIO()
    output_image.save(buffer, format="PNG")

    return {
        "image": base64.b64encode(buffer.getvalue()).decode()
    }
