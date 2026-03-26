import json
import base64
from PIL import Image, ImageDraw
import numpy as np
from typing import List, Dict
import io

def strokes_to_svg(strokes: List[Dict], width: int = 800, height: int = 600) -> str:
    """Convert strokes to SVG path for 3D extrusion."""
    svg = f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">\n'
    
    for stroke in strokes:
        if len(stroke['points']) < 2:
            continue
            
        path_data = f'M {stroke["points"][0]["x"]} {stroke["points"][0]["y"]}'
        for point in stroke['points'][1:]:
            path_data += f' L {point["x"]} {point["y"]}'
        path_data += ' Z'
        
        svg += f'<path d="{path_data}" fill="none" stroke="{stroke["color"]}" stroke-width="4" stroke-linejoin="round" stroke-linecap="round"/>\n'
    
    svg += '</svg>'
    return svg

def svg_to_extruded_gltf(svg_content: str, height: float = 1.0) -> str:
    """Simple SVG extrusion to GLTF (stub - demo cube)."""
    # Real impl: use svgpathtools + trimesh.extrude
    # For demo, return cube GLTF
    gltf = {
        "asset": {"version": "2.0"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0}],
        "meshes": [{
            "primitives": [{
                "attributes": {"POSITION": 0},
                "indices": 0
            }]
        }],
        "accessors": [],  # Cube vertices/indices
        "bufferViews": [],
        "buffers": [{"uri": "data:application/octet-stream;base64,placeholder"}]
    }
    
    gltf_b64 = base64.b64encode(json.dumps(gltf).encode()).decode()
    return gltf_b64

def detect_and_straighten_shapes(image_bytes: bytes) -> Dict:
    """Image → straightened sketch (for main.py)."""
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    draw = ImageDraw.Draw(img)
    
    # Demo: draw straightened square
    draw.rectangle([w//4, h//4, 3*w//4, 3*h//4], outline='black', width=5)
    
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    b64 = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "straightened_sketch_b64": b64,
        "svg": strokes_to_svg([{"points": [{"x":200,"y":200},{"x":600,"y":200},{"x":600,"y":600},{"x":200,"y":600},{"x":200,"y":200}], "color": "#000"}])
    }

def strokes_to_3d(strokes_json: str) -> Dict:
    """New endpoint for air.html strokes."""
    strokes = json.loads(strokes_json)
    svg = strokes_to_svg(strokes)
    
    gltf_b64 = svg_to_extruded_gltf(svg)
    
    return {
        "gltf_b64": gltf_b64,
        "svg": svg,
        "message": f"Extruded {len(strokes)} strokes to 3D model"
    }

