from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'  # Ensure plural
    
    id = db.Column(db.Integer, primary_key=True)
    # Add other user fields as necessary, e.g., name, email, password_hash, role
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # e.g., 'manager', 'customer'
    
    restaurants = db.relationship('Restaurant', backref='manager')
    
    def __repr__(self):
        return f"<User {self.email}>"

class Restaurant(db.Model):
    __tablename__ = 'restaurants'  # Ensure plural
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    categories = db.relationship('Category', secondary='restaurant_categories', back_populates='restaurants')
    reservations = db.relationship('Reservation', back_populates='restaurant', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Category(db.Model):
    __tablename__ = 'categories'  # Ensure plural
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    
    restaurants = db.relationship('Restaurant', secondary='restaurant_categories', back_populates='categories')
    
    def __repr__(self):
        return f"<Category {self.name}>"

# Association table between Restaurant and Category
restaurant_categories = db.Table('restaurant_categories',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class Reservation(db.Model):
    __tablename__ = 'reservations'  # Ensure plural
    
    id = db.Column(db.Integer, primary_key=True)  # reservationID
    reservation_datetime = db.Column(db.DateTime, nullable=False)  # reservationDatetime
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # timestamp
    person_count = db.Column(db.Integer, nullable=False)  # personCount
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)  # restaurantId
    name = db.Column(db.String(100), nullable=False)  # name
    status = db.Column(db.String(20), nullable=False, default='pending')  # status
    
    restaurant = db.relationship('Restaurant', back_populates='reservations')
    
    def __repr__(self):
        return f"<Reservation {self.id} for {self.name} at {self.reservation_datetime}>"
