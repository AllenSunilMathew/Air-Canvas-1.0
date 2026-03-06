

STYLE_MAP = {
    "outline": {
        "positive": (
            "extremely clean and accurate outline, "
            "crisp technical line art, precise edges, "
            "high contrast black lines on white background, no color fill, "
            "industrial design sketch, architectural drawing, "
            "perfect proportions, vector-like precision, "
            "minimalist, sharp focus, no shading or texture"
        ),
        "negative": (
            "photo, photorealistic, texture, shading, color, "
            "cartoon, anime, painting, drawing, blur, "
            "noise, grain, low detail, filled areas, gradients"
        )
    },

    "realistic": {
        "positive": (
            "ultra photorealistic real-world object, "
            "hyper-detailed 8K resolution, ultra high detail, "
            "professional DSLR photography, physically accurate materials, "
            "realistic reflections, global illumination, natural soft lighting, "
            "depth of field, cinematic composition, sharp focus, "
            "intricate textures, lifelike proportions, bokeh effect"
        ),
        "negative": (
            "cartoon, anime, illustration, painting, drawing, "
            "cgi, low resolution, blurry, noisy, unrealistic, "
            "oversaturated, distorted, flat lighting, abstract"
        )
    },

    "animated": {
        "positive": (
            "high quality 3D animated render, "
            "stylized 3D geometry, rounded bubble-like shapes, "
            "smooth curved surfaces, soft beveled edges, "
            "volumetric depth, subsurface scattering, "
            "soft global illumination, studio animation lighting, "
            "vibrant colorful materials, high saturation, "
            "pixar-style, disney-style, 4K animated movie quality, "
            "expressive character design, dynamic poses"
        ),
        "negative": (
            "photorealistic, real photo, flat illustration, "
            "2D drawing, line art, low poly, dull colors, "
            "harsh shadows, noisy, grainy, realistic textures, "
            "low saturation, static, boring composition"
        )
    }
}

SAFETY_NEGATIVE = (
    "human, person, people, face, hand, body, skin, portrait"
)

def enhance_prompt(caption: str, colors: list, style: str):
    style_cfg = STYLE_MAP.get(style, STYLE_MAP["realistic"])

    color_text = ""
    if colors:
        color_text = "with " + ", ".join(colors) + " colors"

    prompt = (
        f"{caption}, {color_text}, "
        f"{style_cfg['positive']}, "
        "masterpiece, best quality, ultra high detail"
    )

    negative_prompt = (
        style_cfg["negative"]
        + ", "
        + SAFETY_NEGATIVE
        + ", low quality, worst quality, jpeg artifacts"
    )

    return prompt, negative_prompt
