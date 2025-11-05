from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_token(email):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(email, salt="email-confirm-salt")

def confirm_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="email-confirm-salt", max_age=expiration)
    except Exception:
        return False
