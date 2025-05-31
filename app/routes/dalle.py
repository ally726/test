# Original file: final 2/app/routes/dalle.py
# Action: Modify
# Reason: Fetch Palette by palette_id, then pass its hex_list, name, and description to the modified dalle_service.generate_image.
# --- MODIFIED app/routes/dalle.py ---
# app/routes/dalle.py
"""DALL·E generation endpoints.

Exposes one POST endpoint:

    POST /api/dalle/generate
        {
            "palette_id": 1,             # required - to fetch colors, name, description
            "context": "ppt",            # required – key defined in prompt_map.py
            "size": "512x512"            # optional – (Note: size handling is API specific for SD3)
        }

Returns on success (HTTP 200):
        {
            "url": "data:image/png;base64,...", # image URI
            "prompt": "…",                # exact prompt sent to Stability AI
            "palette_id": 1               # palette_id from the request
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
from app.models import Palette # Required to fetch palette details

bp = Blueprint("dalle", __name__, url_prefix="/api/dalle")


@bp.post("/generate")
def generate():
    """Generate an image using colors from a palette specified by palette_id.
    """
    data: dict | None = request.get_json(silent=True)
    if not data:
        return jsonify({"error_code": "INVALID_JSON", "message": "Invalid JSON payload."}), 400

    palette_id_from_request = data.get("palette_id")
    context_from_request = data.get("context")
    size_from_request = data.get("size", "512x512") # Default size

    # Basic validation
    if palette_id_from_request is None: # Ensure palette_id is present
        return jsonify({"error_code": "PARAM_MISSING", "message": "'palette_id' is required."}), 400
    try:
        palette_id_int = int(palette_id_from_request)
    except ValueError:
        return jsonify({"error_code": "INVALID_PARAM", "message": "'palette_id' must be an integer."}), 400

    if not context_from_request or not isinstance(context_from_request, str):
        return jsonify({"error_code": "PARAM_MISSING", "message": "'context' (string) is required."}), 400

    # Fetch Palette from DB
    palette = Palette.query.get(palette_id_int)
    if not palette:
        return jsonify({"error_code": "PALETTE_NOT_FOUND", "message": f"Palette with id {palette_id_int} not found."}), 404

    if not palette.hex_list: # Ensure the palette has colors
        return jsonify({"error_code": "PALETTE_NO_COLORS", "message": f"Palette with id {palette_id_int} has no colors defined."}), 400

    try:
        # Call service with hex_list, name, and description from the fetched palette
        result_from_service = generate_image(
            hex_list=palette.hex_list,
            context=context_from_request,
            size=size_from_request,
            palette_name=palette.name or "Unnamed Palette", # Use palette's name
            palette_description=palette.description or ""  # Use palette's description
        )
        
        # Construct final response, adding back palette_id as per original API design
        final_response = {
            "url": result_from_service.get("url"),
            "prompt": result_from_service.get("prompt"),
            "palette_id": palette_id_int 
        }
        return jsonify(final_response), 200
    
    except ValueError as ve: # For errors like empty hex_list from service layer (should be caught by palette.hex_list check above too)
        return jsonify({"error_code": "INVALID_INPUT", "message": str(ve)}), 400
        
    except RuntimeError as e:
        # Custom errors from dalle_service (e.g., STABILITY_AI_ERROR)
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
# --- END MODIFIED app/routes/dalle.py ---