# app/models.py
from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')  # 'customer' or 'manager'

    # Relationships
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    managed_restaurants = db.relationship('Restaurant', backref='manager', lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    reservations = db.relationship('Reservation', backref='restaurant', lazy=True)

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_datetime = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'confirmed', 'canceled'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    def __repr__(self):
        return f"<Reservation {self.id} - {self.status}>"
