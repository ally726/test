# app/routes/user.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Palette, Favorite

user_bp = Blueprint("user", __name__)

@user_bp.route("/favorites", methods=["GET"])
@jwt_required()
def get_favorites():
    user_id = get_jwt_identity()
    favorites = Favorite.query.filter_by(user_id=user_id).all()

    result = []
    for fav in favorites:
        palette = Palette.query.get(fav.palette_id)
        like_count = Favorite.query.filter_by(palette_id=palette.id).count()
        result.append({
            "id": palette.id,
            "name": palette.name,
            "hex_list": palette.hex_list,
            "description": palette.description,
            "like_count": like_count
        })

    return jsonify(result)
