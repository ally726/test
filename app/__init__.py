# app/__init__.py
from dotenv import load_dotenv
load_dotenv()
from .routes import download


from flask import Flask
from .models import db
from .routes import dalle
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

jwt = JWTManager()

def create_app():
    # Initialize Flask application
    app = Flask(__name__)

    # Load configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Register blueprints
    from .routes.auth import auth_bp
    from .routes.palette import palette_bp
    from .routes.user import user_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(palette_bp, url_prefix="/api/palettes")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(dalle.bp)
    app.register_blueprint(download.bp)

    return app
