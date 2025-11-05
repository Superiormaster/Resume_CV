from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from .extensions import mail, login_manager, db
from .models import Base
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.resume import resume_bp
from .routes.upload import upload_bp
from config import BaseConfig, DB_PATH, Config
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Ensure folders exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)

    # Initialize extensions
    mail.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(main_bp)

    return app