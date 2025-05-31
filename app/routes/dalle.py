# app/routes/dalle.py
"""DALL·E generation endpoints.

Exposes one POST endpoint:

    POST /api/dalle/generate
        {
            "hex_list": ["#FF5733", "#33FF57", "#3357FF"],  # required - color codes
            "context": "ppt",                               # required – key defined in prompt_map.py
            "size": "512x512",                             # optional
            "palette_name": "My Colors",                   # optional
            "palette_description": "Beautiful colors"      # optional
        }

Returns on success (HTTP 200):
        {
            "url": "data:image/png;base64,...", # image URI
            "prompt": "…"                       # exact prompt sent to Stability AI
        }

Error responses use a unified schema:
        {
            "error_code": "…",
            "message": "…"
        }
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app
from app.services.dalle_service import generate_image

bp = Blueprint("dalle", __name__, url_prefix="/api/dalle")


@bp.post("/generate")
def generate():
    """Generate an image using colors from hex_list provided by frontend.
    """
    data: dict | None = request.get_json(silent=True)
    if not data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Invalid JSON payload."}), 400

    hex_list = data.get("hex_list")
    context = data.get("context")
    size = data.get("size", "512x512")
    palette_name = data.get("palette_name", "Custom Palette")
    palette_description = data.get("palette_description", "")

    # Basic validation
    if not hex_list or not isinstance(hex_list, list):
        return jsonify({"error_code": "PARAM_MISSING", "message": "'hex_list' (array) is required."}), 400
    
    if len(hex_list) == 0:
        return jsonify({"error_code": "EMPTY_COLORS", "message": "hex_list cannot be empty."}), 400
    
    # Validate hex color format
    for color in hex_list:
        if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
            return jsonify({"error_code": "INVALID_COLOR", "message": f"Invalid hex color format: {color}. Expected format: #RRGGBB"}), 400

    if not context or not isinstance(context, str):
        return jsonify({"error_code": "PARAM_MISSING", "message": "'context' (string) is required."}), 400

    try:
        # Call service with provided parameters
        result = generate_image(
            hex_list=hex_list,
            context=context,
            size=size,
            palette_name=palette_name,
            palette_description=palette_description
        )
        
        return jsonify(result), 200
    
    except ValueError as ve:
        return jsonify({"error_code": "INVALID_INPUT", "message": str(ve)}), 400
        
    except RuntimeError as e:
        # Custom errors from dalle_service
        err_str = str(e)
        if ":" in err_str and any(known_prefix in err_str for known_prefix in ["STABILITY_AI_HTTP_ERROR", "STABILITY_AI_ERROR"]):
            code, _, message = err_str.partition(":")
        else: 
            code = "DALLE_SERVICE_ERROR"
            message = err_str
        
        return jsonify({"error_code": code.strip(), "message": message.strip()}), 502

    except Exception as e:
        current_app.logger.error(f"Unhandled exception in dalle/generate: {e}", exc_info=True)
        return jsonify({"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred."}), 500