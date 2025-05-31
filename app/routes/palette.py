# app/routes/palette.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Palette, Favorite

palette_bp = Blueprint("palette", __name__)

@palette_bp.route("/", methods=["GET"])
def get_all_palettes():
    palettes = Palette.query.all()
    result = []
    for p in palettes:
        result.append({
            "id": p.id,
            "name": p.name,
            "hex_list": p.hex_list,
            "description": p.description,
            "like_count": Favorite.query.filter_by(palette_id=p.id).count()
        })
    return jsonify(result)


@palette_bp.route("/<int:palette_id>", methods=["GET"])
def get_palette_detail(palette_id):
    p = Palette.query.get_or_404(palette_id)
    like_count = Favorite.query.filter_by(palette_id=palette_id).count()
    return jsonify({
        "id": p.id,
        "name": p.name,
        "hex_list": p.hex_list,
        "description": p.description,
        "like_count": like_count
    })


@palette_bp.route("/<int:palette_id>/favorite", methods=["POST"])
@jwt_required()
def toggle_favorite(palette_id):
    user_id = get_jwt_identity()
    fav = Favorite.query.filter_by(user_id=user_id, palette_id=palette_id).first()

    if fav:
        db.session.delete(fav)
        action = "unfavorited"
    else:
        new_fav = Favorite(user_id=user_id, palette_id=palette_id)
        db.session.add(new_fav)
        action = "favorited"

    db.session.commit()
    like_count = Favorite.query.filter_by(palette_id=palette_id).count()
    return jsonify({"msg": action, "like_count": like_count})
