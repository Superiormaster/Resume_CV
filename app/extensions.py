from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

mail = Mail()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"

engine = None
SessionLocal = None

def init_db(engine_url):
    global engine, SessionLocal
    engine = create_engine(engine_url, connect_args={'check_same_thread': False}, echo=False)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal