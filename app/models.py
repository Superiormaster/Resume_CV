# app/models.py
from datetime import datetime
from app.extensions import db
from sqlalchemy import JSON, event
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    template = db.Column(db.String(200))
    data_json = db.Column(db.Text)
    html_preview = db.Column(db.Text)
    pdf_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    experience = db.Column(JSON, default=list)
    education = db.Column(JSON, default=list)

class UploadedFile(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    message = db.Column(db.Text)
    subject = db.Column(db.String(200), nullable=True)

    type = db.Column(db.String(20))  
    # "contact", "feedback", "report"

    is_read = db.Column(db.Boolean, default=False)
    is_replied = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    resolved = db.Column(db.Boolean, default=False)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stars = db.Column(db.Integer)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

class AppSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email_notifications = db.Column(db.Boolean, default=True)
    contact_email = db.Column( db.Text, nullable=True)
    privacy_policy = db.Column( db.Text, nullable=True)
    premium_policy = db.Column( db.Text, nullable=True)
    share_button = db.Column( db.Text, nullable=True)
    terms_conditions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)