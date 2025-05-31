# debug_prompt.py
import os
from app import create_app
from app.models import db, Palette
from app.services.dalle_service import build_prompt, generate_image

# 1) 启动 Flask
app = create_app()
with app.app_context():
    db.create_all()

    # 2) 拿到第一条 palette
    palette = Palette.query.first()
    if not palette:
        raise RuntimeError("No Palette found in DB!")

    # 3) 构建 prompt 并打印
    prompt = build_prompt("ppt", palette)
    print("=== DEBUG PROMPT ===")
    print(prompt)
    print("====================\n")

    # 4) 用最简化的手动 prompt 测试 API，绕过 build_prompt
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        resp = openai.images.generate(
            prompt="A minimalist abstract background",  # 简化测试
            n=1,
            size="512x512"
        )
        print("Minimal test OK, got URL:", resp.data[0].url)
    except Exception as e:
        print("Minimal test failed:", e)

    # 5) 再试真正的 generate_image
    try:
        result = generate_image(palette.id, context="ppt", size="512x512")
        print("\n>>> generate_image 返回:", result)
    except Exception as e:
        print("\n>>> generate_image 错误:", e)
