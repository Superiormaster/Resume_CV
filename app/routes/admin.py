from flask import (
    Blueprint, render_template, request,
    redirect, current_app, url_for, flash, jsonify
)
from datetime import datetime
from flask_login import (
    login_user, logout_user,
    login_required
)
from flask_mail import Message as MailMessage
from app.utils.decorators import admin_required, role_required
from app.utils.db_helpers import safe_commit
from app.models import Post, Admin, AppSettings, Category, Label, Tag, CaptionHistory, User, Comment, ContactMessage, Repost
from app.extensions import db, mail
from flask_login import current_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
from app.utils.cloudinary import upload_image_file
from werkzeug.utils import secure_filename
from slugify import slugify
import os

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="../templates/admin"
)

# Admin login
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data
        password = form.password.data

        admin = Admin.query.filter(
            (Admin.username == identifier) | (Admin.email == identifier)
        ).first()

        if not admin or not admin.check_password(password):
            flash("Invalid username/email or password", "danger")
            return redirect(url_for("admin.login"))

        login_user(admin)
        flash("Welcome Admin", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/login.html", form=form)

@admin_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_password = request.form.get("current_password").strip()
        new_password = request.form.get("new_password").strip()
        confirm_password = request.form.get("confirm_password").strip()
        # Check current password
        if not check_password_hash(current_user.password, form.current_password.data):
            flash("Current password is incorrect", "error")
            return redirect(url_for("admin.change_password"))

        if form.new_password.data != form.confirm_password.data:
            flash("New passwords do not match", "error")
            return redirect(url_for("admin.change_password"))

        # Update password
        current_user.password = generate_password_hash(form.new_password.data)
        if not safe_commit():
          print("Failed to change password")
        flash("Password updated successfully!", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/change_password.html", form=form)

@admin_bp.route("/dashboard")
@login_required
def dashboard():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "all").lower()

    # Start query with all posts
    query = Post.query

    # Search by title if query provided
    if q:
        query = query.filter(Post.title.ilike(f"%{q}%"))

    # Filter by status if not "all"
    if status == "published":
        query = query.filter_by(status="published")
    elif status == "draft":
        query = query.filter_by(status="draft")
    elif status == "pending":
        query = query.filter_by(status="pending")
    elif status == "rejected":
        query = query.filter_by(status="rejected")

    # Order by newest first
    posts = query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)

    return render_template(
        "admin/dashboard.html",
        posts=posts,
        q=q,
        status=status
    )

@admin_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image_route():
    current_app.logger.info("Upload route hit")
    file = request.files.get("image")
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    url = upload_image_file(file, folder="SuperiorNews/editor")  # <-- use your helper function
    if not url:
        return jsonify({"error": "Upload failed"}), 500

    return jsonify({"location": url}), 200

@admin_bp.route("/messages")
@login_required
def admin_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    message = ContactMessage.query.filter_by(type="report")
    mess = ContactMessage.query.filter_by(is_replied=False)
    return render_template("admin/messages.html", mess=mess, message=message, messages=messages)

@admin_bp.route("/messages/<int:id>/reply", methods=["POST"])
@login_required
@csrf.exempt
def reply_message(id):
    msg = ContactMessage.query.get_or_404(id)

    reply_text = request.form.get("reply")

    """mail_msg = MailMessage(
        subject=f"Re: {msg.subject or 'Your message'}",
        recipients=[msg.email],
        body=reply_text
    )

    mail.send(mail_msg)"""
    
    success = send_email(
        msg.email,
        f"Re: {msg.subject or 'Your message'}",
        reply_text
    )

    if success:
      msg.is_replied = True
      if not safe_commit():
        print("Failed to send message")
  
      flash("Reply sent successfully.", "success")
    else:
      flash(
          "Reply saved, but email could not be sent. Please check your internet connection.",
          "warning"
      )

    return redirect(url_for("admin.admin_messages"))

@admin_bp.route("/messages/<int:id>")
@login_required
def view_message(id):
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = True
    if not safe_commit():
        print("Failed to read messages")

    return render_template("admin/message_detail.html", msg=msg)