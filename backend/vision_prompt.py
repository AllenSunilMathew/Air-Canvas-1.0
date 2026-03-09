
import torch, io
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = BlipProcessor.from_pretrained(
    "Salesforce/blip-image-captioning-base"
)
model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base"
).to(device)

BLOCKED_WORDS = [
    "person", "man", "woman", "boy", "girl",
    "hand", "face", "body", "human", "people"
]

def sketch_to_prompt(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = processor(image, return_tensors="pt").to(device)
    out = model.generate(**inputs, max_new_tokens=40)

    caption = processor.decode(out[0], skip_special_tokens=True)

    for w in BLOCKED_WORDS:
        caption = caption.replace(w, "")

    return caption.strip()