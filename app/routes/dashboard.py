from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from app.models import Resume, UploadedFile

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/dashboard')
def dashboard():
    """User dashboard to view saved resumes and uploads."""
    resumes = Resume.query.filter_by().order_by(Resume.created_at.desc()).all()
    uploads = UploadedFile.query.filter_by().order_by(UploadedFile.uploaded_at.desc()).all()

    if not resumes:
        flash("You haven't created any resumes yet.", "info")

    return render_template('dashboard.html', resumes=resumes, uploads=uploads)