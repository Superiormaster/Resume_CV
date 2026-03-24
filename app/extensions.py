# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask import jsonify, url_for, redirect, flash

db = SQLAlchemy()