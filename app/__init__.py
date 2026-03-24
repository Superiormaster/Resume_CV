from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from .routes.main import main_bp
from .routes.dashboard import dashboard_bp
from .routes.resume import resume_bp
from .routes.upload import upload_bp
from config import Config
import os
from flask_migrate import Migrate
from app.routes.meta import meta_bp
from app.extensions import db
from app.models import AppSettings
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure folders exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)

    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(meta_bp)
    
    @app.context_processor
    def inject_year():
        return {'year': datetime.now().year}
    
    @app.context_processor
    def inject_settings():
        return dict(AppSettings=AppSettings)

    return app