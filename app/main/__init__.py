# app/main/__init__.py
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes

from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))