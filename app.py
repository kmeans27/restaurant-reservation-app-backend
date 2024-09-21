# app.py
from app import create_app, db
from flask_migrate import Migrate

app = create_app()

# Initialize Flask-Migrate here
migrate = Migrate(app, db)

# Import models to ensure they are registered
from app import models
