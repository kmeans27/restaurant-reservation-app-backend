# config.py
import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    #SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SECRET_KEY = 'your_secret_key' # NOT SECURE FOR PRODUCTION!!!!
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True  # Enable debug mode
