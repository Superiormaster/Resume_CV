from flask import Blueprint, request, render_template, redirect, url_for, flash
import traceback
from flask_mail import Message
from app.extensions import db, mail
from app.models import ContactMessage, Rating, AppSettings
from sqlalchemy import func

meta_bp = Blueprint("meta_bp", __name__, url_prefix="/meta")

# ----- CONTACT US -----
@meta_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not email or not message:
            flash("Email and message are required.", "danger")
            return redirect(url_for("meta_bp.contact"))
            
        # Save to DB
        msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(msg)
        db.session.commit()
        
        # Send email
        try:
          msg = Message(
              subject="New Contact Message",
              sender="ejeziepaschal@gmail.com",
              
              recipients=["ejeziepaschal@gmail.com"],
              body=f"""
New message from your Resume app:

Name: {name}
Email: {email}

Message:
{message}
              """
          )
          mail.send(msg)
          flash("Message sent successfully!", "success")
        except Exception as e:
          traceback.print_exc()
          flash("Message saved, but email failed.", "warning")

        return redirect(url_for("meta_bp.contact"))
    return render_template("meta/contact.html")

# ----- RATING -----
@meta_bp.route("/rate", methods=["GET", "POST"])
def rate():
    if request.method == "POST":
        stars = int(request.form.get("stars"))
        comment = request.form.get("comment")

        if stars < 1 or stars > 5:
            flash("Invalid rating.", "danger")
            return redirect(url_for("meta_bp.rate"))

        rating = Rating(stars=stars, comment=comment)
        db.session.add(rating)
        db.session.commit()
        flash("Thank you for your rating!", "success")
        return redirect(url_for("meta_bp.rate"))

    avg = db.session.query(func.avg(Rating.stars)).scalar() or 0
    count = db.session.query(func.count(Rating.id)).scalar() or 0
    return render_template("meta/rate.html", average=round(avg, 2), count=count)


# ----- USER SETTINGS -----
@meta_bp.route("/settings", methods=["GET", "POST"])
def settings():
    settings = AppSettings.query.first()

    if request.method == "POST":
        email_notifications = bool(request.form.get("email_notifications"))
        privacy_policy = request.form.get("privacy_policy")
        premium_policy = request.form.get("premium_policy")
        contact_email = request.form.get("contact_email")
        share_button = request.form.get("share_button")

        if not settings:
          settings = AppSettings(
            email_notifications=email_notifications,
            privacy_policy=privacy_policy,
            premium_policy=premium_policy,
            contact_email=contact_email,
            share_button=share_button
          )
          db.session.add(settings)
        else:
          settings.email_notifications = email_notifications
          settings.privacy_policy = privacy_policy
          settings.premium_policy = premium_policy
          settings.contact_email = contact_email
          settings.share_button = share_button
        db.session.commit()
        flash("Settings saved!", "success")
        return redirect(url_for("meta_bp.settings"))

    return render_template("meta/settings.html", settings=settings)


# ----- PRIVACY -----
@meta_bp.route("/privacy")
def privacy():
    settings = AppSettings.query.first()
    return render_template("meta/privacy.html", settings=settings)
    
# ----- SHARE_BUTTON -----
@meta_bp.route("/share")
def share():
  settings = AppSettings.query.first()
  return render_template("meta/share.html", settings=settings)

# ----- PREMIUM -----
@meta_bp.route("/premium")
def premium():
    settings = AppSettings.query.first()
    return render_template("meta/premium.html")