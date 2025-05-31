# Original file: final 2/app/services/dalle_service.py
# Action: Modify
# Reason: Modify generate_image and build_prompt. generate_image will take hex_list, name, description directly. No DB interaction for saving generated_url.
# --- MODIFIED app/services/dalle_service.py ---
# -*- coding: utf-8 -*-
"""DreamStudio Image Generation Service Layer

* Builds the final prompt (context template + palette information)
* Uses Redis *if configured*; otherwise falls back to an in-memory cache
* Wraps the Stability AI DreamStudio v2beta call using multipart/form-data,
  adds simple caching, error handling.
  Generated URIs are NOT persisted to the Palette model by this service directly.
"""
from __future__ import annotations

import collections
import hashlib
import os
import redis
import requests
from typing import Protocol, runtime_checkable
from app.utils.prompt_map import map_scene
# Palette and db are not imported as this service will not interact with the DB directly for Palette model.
# from app.models import Palette, db

# ---------------------------------------------------------------------------
# 0. Configuration ----------------------------------------------------------
# ---------------------------------------------------------------------------

stability_api_key = os.getenv("STABILITY_API_KEY")
if not stability_api_key:
    raise RuntimeError("STABILITY_API_KEY is missing. Add it to your environment or .env file.")

# ---------------------------------------------------------------------------
# 1. Cache ------------------------------------------------------------------
# ---------------------------------------------------------------------------

@runtime_checkable
class CacheLike(Protocol):
    def get(self, key: str) -> bytes | None: ...
    def setex(self, key: str, ttl: int, value: str) -> None: ...

class DummyCache(collections.UserDict):
    def get(self, key: str):
        value = super().get(key)
        if value is None:
            return None
        return value if isinstance(value, bytes) else str(value).encode()

    def setex(self, key: str, ttl: int, value: str):
        self[key] = value

def _create_cache() -> CacheLike:
    url = os.getenv("REDIS_URL")
    if url:
        try:
            return redis.from_url(url)
        except Exception as exc:
            print(f"[dalle_service] Redis connection failed: {exc}. Falling back to DummyCache.")
    else:
        print("[dalle_service] REDIS_URL not set – using DummyCache (in‑memory).")
    return DummyCache()

rds: CacheLike = _create_cache()

# ---------------------------------------------------------------------------
# 2. Helper -----------------------------------------------------------------
# ---------------------------------------------------------------------------

def build_prompt(context: str, hex_list: list[str], name: str, description: str) -> str:
    base = map_scene(context)
    colors = ", ".join(hex_list)
    palette_str = f"Use only these colors: {colors}. Palette name: {name} - {description}."
    return base.format(palette=palette_str)

def _cache_key(prompt: str, size: str) -> str:
    h = hashlib.md5(f"{prompt}_{size}".encode()).hexdigest()
    return f"dalle:{h}"

# ---------------------------------------------------------------------------
# 3. Public API -------------------------------------------------------------
# ---------------------------------------------------------------------------

import base64

def generate_image(
    hex_list: list[str],
    context: str,
    size: str, # Size parameter from the route, its effect depends on StabilityAI API
    palette_name: str,
    palette_description: str
) -> dict:
    if not hex_list:
        raise ValueError("Hex list cannot be empty for image generation.")

    prompt = build_prompt(context, hex_list, palette_name, palette_description)
    key = _cache_key(prompt, size) # Size is used in cache key for differentiation

    if cached := rds.get(key):
        return {"url": cached.decode(), "prompt": prompt}

    url = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Accept": "image/*",
    }
    
    form_data = {
        "prompt": prompt,
        "output_format": "png",
        # For SD3, 'size' (e.g., "512x512") might not be a direct form field.
        # It might be an aspect_ratio or width/height.
        # We are passing `size` from the route, but not directly adding it to `form_data` here
        # unless the Stability AI API specifically takes a 'size' field in this format for SD3.
        # If specific dimensions are needed, they'd be passed like:
        # "aspect_ratio": "1:1" or "width": 512, "height": 512
        # The current implementation relies on the default behavior of the API if size is not explicit.
    }
    files = {'none': ''} # Required for multipart/form-data if no initial image

    try:
        resp = requests.post(url, headers=headers, data=form_data, files=files, timeout=60)
        resp.raise_for_status()

        b64_image = base64.b64encode(resp.content).decode("utf-8")
        img_uri = f"data:image/png;base64,{b64_image}"

    except requests.exceptions.HTTPError as http_err:
        error_message = f"STABILITY_AI_HTTP_ERROR: {http_err.response.status_code}"
        try:
            error_details = http_err.response.json()
            if "errors" in error_details:
                 error_message += f" - Details: {'; '.join(error_details['errors'])}"
            elif "message" in error_details: # some APIs use 'message'
                 error_message += f" - Details: {error_details['message']}"
            elif "name" in error_details and "message" in error_details: # another possible format
                 error_message += f" - Name: {error_details['name']}, Message: {error_details['message']}"

        except ValueError: # If response is not JSON
            error_message += f" - Response body: {http_err.response.text}"
        raise RuntimeError(error_message) from http_err
    except Exception as exc:
        raise RuntimeError(f"STABILITY_AI_ERROR: An unexpected error occurred during image generation - {exc}") from exc

    try:
        rds.setex(key, 43200, img_uri)  # Cache for 12 hours
    except Exception as exc:
        print(f"[dalle_service] Cache write failed: {exc}")

    # Removed saving generated_url to DB as per user request ("不需要考慮下載的問題")
    # if palette_id:
    #     try:
    #         palette_to_update: Palette | None = Palette.query.get(palette_id)
    #         ... (db update logic removed) ...
    #     except Exception as exc:
    #         ...

    return {"url": img_uri, "prompt": prompt}
# --- END MODIFIED app/services/dalle_service.py ---