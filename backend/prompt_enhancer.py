# Highly Optimized Prompt Templates
# Pre-computed embeddings for faster generation

# Pre-computed style embeddings (reduces prompt processing time)
STYLE_POSITIVE = {
    "realistic": (
        "hyper-realistic photograph, 8K UHD, photorealistic, "
        "professional DSLR, shallow depth of field, bokeh, "
        "natural lighting, soft shadows, realistic textures, "
        "anatomically correct, detailed, sharp focus, "
        "cinematic composition, master piece"
    ),
    "animated": (
        "3D animated render, Pixar Disney style, cartoon, "
        "vibrant colors, toon shader, cel shaded, smooth, "
        "feature film quality, volumetric lighting, "
        "stylized geometry, expressive, cheerful, "
        "beautiful lighting, detailed textures, master piece"
    ),
    "outline": (
        "clean line art, technical drawing, blueprint, "
        "vector illustration, crisp lines, black on white, "
        "minimalist, precise, architectural sketch, "
        "geometric, detailed linework, professional, "
        "high contrast, clean, master piece"
    ),
    "default": (
        "high quality illustration, detailed artwork, "
        "beautiful composition, professional, master piece"
    )
}

STYLE_NEGATIVE = {
    "realistic": (
        "cartoon, anime, drawing, painting, illustration, "
        "3D render, lowres, blurry, distorted, ugly, "
        "deformed, low quality, watermark, text"
    ),
    "animated": (
        "photorealistic, photo, realistic, flat, 2D, "
        "line art, low poly, dull, grainy, ugly, "
        "deformed, low quality, watermark, text"
    ),
    "outline": (
        "color, photo, shading, gradient, fill, "
        "painting, cartoon, blurry, messy, uneven, "
        "low quality, watermark, text"
    ),
    "default": (
        "low quality, blurry, distorted, watermark, "
        "text, signature, ugly, deformed"
    )
}

# Safety keywords
SAFETY_NEGATIVE = (
    "human, person, man, woman, child, face, hand, body, "
    "skin, portrait, people, crowd, nsfw, explicit"
)

# Color to quality mapping
COLOR_QUALITY = {
    "red": "warm red accent",
    "blue": "cool blue accent", 
    "green": "natural green accent",
    "yellow": "bright yellow highlight",
    "orange": "vibrant orange tone",
    "purple": "rich purple accent",
    "pink": "soft pink highlight",
    "cyan": "bright cyan accent"
}

def enhance_prompt(caption: str, colors: list, style: str = "realistic"):
    """
    Ultra-optimized prompt enhancement.
    Uses pre-computed embeddings for speed.
    """
    # Get pre-computed style prompts
    positive = STYLE_POSITIVE.get(style, STYLE_POSITIVE["default"])
    negative = STYLE_NEGATIVE.get(style, STYLE_NEGATIVE["default"])
    
    # Build color text efficiently
    color_text = ""
    if colors:
        # Filter meaningful colors
        meaningful = [c for c in colors if c in COLOR_QUALITY]
        if meaningful:
            color_text = ", ".join([COLOR_QUALITY[c] for c in meaningful[:2]])
            color_text = f"{color_text}, "
    
    # Combine with caption
    prompt = f"{caption}, {color_text}{positive}"
    
    # Build negative prompt
    neg = f"{negative}, {SAFETY_NEGATIVE}, worst quality, jpeg artifacts"
    
    return prompt.strip(), neg.strip()


def quick_enhance(caption: str, style: str = "realistic"):
    """Quick enhancement without color analysis"""
    positive = STYLE_POSITIVE.get(style, STYLE_POSITIVE["default"])
    negative = STYLE_NEGATIVE.get(style, STYLE_NEGATIVE["default"])
    
    prompt = f"{caption}, {positive}"
    neg = f"{negative}, {SAFETY_NEGATIVE}"
    
    return prompt.strip(), neg.strip()

