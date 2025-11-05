from flask import Blueprint
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models import UploadedFile

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route("/upload", methods=["POST"])
@login_required
def upload_file():
    """Upload a resume file."""
    if "file" not in request.files:
        flash("No file part.", "danger")
        return redirect(request.referrer or url_for("dashboard"))

    file = request.files["file"]

    if file.filename == "":
        flash("No file selected.", "warning")
        return redirect(request.referrer or url_for("dashboard"))

    if not allowed_file(file.filename):
        flash("Unsupported file type.", "danger")
        return redirect(request.referrer or url_for("dashboard"))

    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    db = SessionLocal()
    try:
        uploaded = UploadedFile(
            user_id=current_user.id,
            filename=filename,
            filepath=save_path
        )
        db.add(uploaded)
        db.commit()
        flash("File uploaded successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error saving upload: {e}", "danger")
    finally:
        db.close()

    return redirect(url_for("dashboard"))

@upload_bp.route("/uploads/download/<int:file_id>")
@login_required
def download_uploaded(file_id):
    db = SessionLocal()
    try:
        f = db.query(UploadedFile).filter_by(id=file_id, user_id=current_user.id)
        if not f:
            flash("File not found.", "danger")
            return redirect(request.referrer or url_for("dashboard"))

        return send_file(f.filepath, as_attachment=True, download_name=f.filename)
    except Exception as e:
        flash(f"Error downloading file: {e}", "danger")
        return redirect(request.referrer or url_for("dashboard"))
    finally:
        db.close()

@upload_bp.route("/uploads/delete/<int:file_id>")
@login_required
def delete_uploaded(file_id):
    db = SessionLocal()
    try:
        f = db.query(UploadedFile).filter_by(id=file_id, user_id=current_user.id).first()
        if not f:
            flash("File not found.", "danger")
            return redirect(request.referrer or url_for("dashboard"))

        if os.path.exists(f.filepath):
            os.remove(f.filepath)

        db.delete(f)
        db.commit()
        flash("File deleted successfully!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting file: {e}", "danger")
    finally:
        db.close()

    return redirect(url_for("dashboard"))
