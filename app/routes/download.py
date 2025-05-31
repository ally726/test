# app/routes/download.py
from flask import Blueprint, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required
from app.models import Palette
import os, requests
import base64

bp = Blueprint("download", __name__, url_prefix="/api/download")

@bp.get("/<int:palette_id>")
def download_image(palette_id):
    palette = Palette.query.get(palette_id)
    if not palette or not getattr(palette, "generated_url", None):
        return jsonify(error_code="NOT_FOUND", message="Image not found"), 404

    # 檢查是否是 base64 data URI
    if palette.generated_url.startswith("data:image/png;base64,"):
        try:
            # 去除前綴並 decode
            img_b64 = palette.generated_url.replace("data:image/png;base64,", "")
            img_bytes = base64.b64decode(img_b64)

            # 儲存快取檔案
            cache_dir = os.path.join(current_app.instance_path, "images")
            os.makedirs(cache_dir, exist_ok=True)
            local_path = os.path.join(cache_dir, f"{palette_id}.png")

            # 寫入圖片檔案
            with open(local_path, "wb") as f:
                f.write(img_bytes)

            return send_file(local_path, as_attachment=True)

        except Exception:
            return jsonify(error_code="DECODE_FAIL", message="Cannot decode base64 image"), 500

    else:
        # 如果是普通 URL，保留你原本的邏輯
        cache_dir = os.path.join(current_app.instance_path, "images")
        os.makedirs(cache_dir, exist_ok=True)
        local_path = os.path.join(cache_dir, f"{palette_id}.png")

        if not os.path.exists(local_path):
            try:
                resp = requests.get(palette.generated_url, timeout=10)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
            except Exception:
                return jsonify(error_code="FETCH_FAIL", message="Cannot fetch image"), 502

        return send_file(local_path, as_attachment=True)
