import os
from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Homepage."""
    base_dir = current_app.root_path  # safer than BASE_DIR in modular apps
    templates_path = os.path.join(base_dir, 'templates', 'templates_variants')
    templates = os.listdir(templates_path)
    return render_template('index.html', templates=templates)
