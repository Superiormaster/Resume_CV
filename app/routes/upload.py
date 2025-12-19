import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models import UploadedFile

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# Allowed extensions
def allowed_file(filename):
    allowed = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed

# -------------------
# Upload Route
# -------------------
@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        flash("No file part.", "danger")
        return redirect(request.referrer or url_for("dashboard_bp.dashboard"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.", "warning")
        return redirect(request.referrer or url_for("dashboard_bp.dashboard"))

    if not allowed_file(file.filename):
        flash("Unsupported file type.", "danger")
        return redirect(request.referrer or url_for("dashboard_bp.dashboard"))

    # Generate unique filename
    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
    
    # Correct RELATIVE PATH
    rel_path = f"static/uploads/{filename}"
    full_path = os.path.join(current_app.root_path, rel_path)

    # Ensure folder exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Save file
    file.save(full_path)

    # Save DB record
    uploaded = UploadedFile(filename=filename, filepath=rel_path)
    db.session.add(uploaded)
    db.session.commit()

    flash("File uploaded successfully!", "success")
    return redirect(url_for("dashboard_bp.dashboard"))

# -------------------
# Download Route
# -------------------
@upload_bp.route("/uploads/download/<int:file_id>")
def download_uploaded(file_id):
    file = UploadedFile.query.get(file_id)

    if not file:
        flash("File not found.", "danger")
        return redirect(request.referrer or url_for("dashboard_bp.dashboard"))

    full_path = os.path.join(current_app.root_path, file.filepath)
    return send_file(full_path, as_attachment=True, download_name=file.filename)

# -------------------
# Delete Route
# -------------------
@upload_bp.route("/uploads/delete/<int:file_id>")
def delete_uploaded(file_id):
    file = UploadedFile.query.get(file_id)

    if not file:
        flash("File not found.", "danger")
        return redirect(request.referrer or url_for("dashboard_bp.dashboard"))

    full_path = os.path.join(current_app.root_path, file.filepath)

    # Remove file
    if os.path.exists(full_path):
        os.remove(full_path)

    db.session.delete(file)
    db.session.commit()

    flash("File deleted successfully!", "success")
    return redirect(url_for("dashboard_bp.dashboard"))