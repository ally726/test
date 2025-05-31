# app/routes/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import db, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        token = create_access_token(identity=str(user.id))
        return jsonify(access_token=token), 200

    return jsonify({"msg": "Invalid email or password"}), 401


@auth_bp.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify(logged_in_as=user_id), 200
