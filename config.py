import os

BASE_DIR = os.path.abspath(os.path.dirname( __file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'app.db')

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.getcwd(), 'data', 'app.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    RESUME_FOLDER = os.environ.get('RESUME_FOLDER', os.path.join(BASE_DIR, 'resumes'))
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

class Config(BaseConfig):
    DEBUG = True
