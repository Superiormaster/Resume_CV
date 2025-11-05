from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import mail, SessionLocal
from app.models import SessionLocal
from flask_mail import Message
from app.utils.token_utils import generate_token, confirm_token

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        name = request.form.get("name", "").strip().lower()

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for("auth.register"))

        db = SessionLocal()
        if db.query(User).filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for("auth.login"))

        user = User(email=email, password_hash=generate_password_hash(password), name=name)
        db.add(user)
        db.commit()

        token = generate_token(email)
        verify_url = url_for("auth.verify_email", token=token, _external=True)

        msg = Message("Confirm Your Email", sender="your_email@gmail.com", recipients=[email])
        msg.body = f"Click to verify: {verify_url}"
        mail.send(msg)

        flash("A verification email has been sent.", "info")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        password = request.form.get('password')

        if not email or not password:
            flash("Please enter both email and password.", "login")
            return render_template(url_for('auth.login'))

        with SessionLocal() as db:
            user = db.query(User).filter_by(email=email).first()

            if not user or not check_password_hash(user.password_hash, password):
                flash("Invalid Credentials", "login danger")
                return render_template('login.html')

            # Log in the user
            login_user(user)
            flash('Login successful!', 'dashboard')

            # Redirect to dashboard or the 'next' page if present
            next_page = request.args.get('next')
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# ---------------- Token verification ------------------
""" Learn everything here """
@auth_bp.route('/verify/<token>')
def verify_email(token):
    try:
        email = confirm_token(token)
    except Exception:
        flash('Verification link is invalid or expired.', 'danger')
        return redirect(url_for('auth_login'))

    db = SessionLocal()
    user = db.query(User).filter_by(email=email).first()

    if not user:
        flash('User not found or invalid token.', 'danger')
        db.close()
        return redirect(url_for('auth.register'))

    if user.verified:
        flash('Account already verified. Please login!', 'info')
    else:
        user.verified = True
        db.commit()
        flash('Your account has been verified. You can now login!', 'success')

    db.close()
    return redirect(url_for('auth.login'))

# --- Resend Verification ---
@auth_bp.route('/resend-verification')
def resend_verification():
    if not current_user.is_authenticated:
        flash('Please log in first.', 'info')
        return redirect(url_for('login'))

    if current_user.verified:
        flash('Account already verified.', 'info')
        return redirect(url_for('auth.login'))

    token = generate_token(current_user.email)
    verify_url = url_for('verify_email', token=token, _external=True)

    msg = Message('Confirm Your Email', recipients=[current_user.email])
    msg.body = f'Click to verify your email: {verify_url}'
    mail.send(msg)

    flash('A new verification email has been sent.', 'info')
    return redirect(url_for('dashboard'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user."""
    logout_user()
    flash("You have been logged out.", "index info")
    return redirect(url_for('index'))