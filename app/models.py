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

    # New fields for geographical coordinates
    latitude = db.Column(db.Float, nullable=True)   # TODO: Consider setting nullable=False after seeding
    longitude = db.Column(db.Float, nullable=True)  # TODO: Consider setting nullable=False after seeding
    
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
# New FrontendUser Model
class FrontendUser(db.Model):
    __tablename__ = 'frontend_users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique identifier from frontend
    email = db.Column(db.String(120), unique=True, nullable=True)  # TODO: Set nullable=False after validation
    password = db.Column(db.String(128), nullable=True)  # TODO: Set nullable=False and handle hashing
    name = db.Column(db.String(100), nullable=True)  # TODO: Set nullable=False after validation
    
    reservations = db.relationship('Reservation', back_populates='frontend_user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<FrontendUser {self.user_id}>"

# added frontend_user_id to Reservation
class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    reservation_datetime = db.Column(db.DateTime, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    person_count = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    frontend_user_id = db.Column(db.Integer, db.ForeignKey('frontend_users.id'), nullable=True)
    
    restaurant = db.relationship('Restaurant', back_populates='reservations')
    frontend_user = db.relationship('FrontendUser', back_populates='reservations')
    
    def __repr__(self):
        return f"<Reservation {self.id} for {self.name} at {self.reservation_datetime}>"


