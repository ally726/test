# app/__init__.py
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from .routes import dalle
from flask_cors import CORS

def create_app():
    # Initialize Flask application
    app = Flask(__name__)

    # Initialize CORS
    CORS(app)

    # Register blueprints
    app.register_blueprint(dalle.bp)

    return app