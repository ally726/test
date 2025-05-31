# app/utils/prompt_map.py
"""
Define mapping between user-selected 'context' and a base prompt template.

The base prompt *must* contain `{palette}` placeholder, which will be
filled by dalle_service.build_prompt().
"""

SCENE_PROMPTS = {
    "interior": (
        "Scandinavian living room interior render, cozy and bright, {palette}"
    ),
    "ppt": (
        "A clean, minimalist PowerPoint slide background with soft gradients "
        "and ample white space. {palette}"
    ),
    "fashion": (
        "A modern streetwear outfit concept illustration on a white backdrop, {palette}"
    ),
    "dog": (
        "A cute dog sitting in a field of flowers, watercolor style. {palette}"
    ),
    "cat": (
        "An elegant cat sitting on a windowsill, soft lighting and warm tones. {palette}"
    ),
    "coffee": (
        "A cozy coffee shop scene with latte art, wooden furniture, and warm lighting. {palette}"
    ),
    "space": (
        "A vibrant galaxy scene with stars, planets, and cosmic dust, digital painting style. {palette}"
    ),
    "forest": (
        "A serene forest landscape with sunrays filtering through tall trees. {palette}"
    )
}

def map_scene(scene: str) -> str:
    """Return the template string for a given context key."""
    scene = (scene or "").strip()
    return SCENE_PROMPTS.get(scene, scene)   # fallback：直接回傳原字串
