from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from .extensions import db
from .routes.main import main_bp
from .routes.dashboard import dashboard_bp
from .routes.resume import resume_bp
from .routes.upload import upload_bp
from config import DB_PATH, Config
import os
from flask_migrate import Migrate
from app.routes.meta import meta_bp
from app.extensions import mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Ensure folders exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["RESUME_FOLDER"], exist_ok=True)
    
    db.init_app(app)
    mail.init_app(app)
    migrate = Migrate(app, db)
    
    with app.app_context():
      db.create_all()

    # Register blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(meta_bp)
    
    print("MAIL USER:", app.config["MAIL_USERNAME"])
    print("MAIL PASS SET:", bool(app.config["MAIL_PASSWORD"]))
    print("SMTP SERVER:", app.config["MAIL_SERVER"])
    print("SMTP PORT:", app.config["MAIL_PORT"])

    return app