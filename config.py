import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname( __file__))

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(BASE_DIR, 'uploads'))
    RESUME_FOLDER = os.environ.get('RESUME_FOLDER', os.path.join(BASE_DIR, 'resumes'))

class Config(BaseConfig):
    DEBUG = True
