from datetime import datetime
from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Association table between Restaurant and Category
restaurant_categories = db.Table(
    'restaurant_categories',
    db.Column('restaurant_id', db.Integer, db.ForeignKey('restaurants.id'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=True)

    # Relationships
    restaurant = db.relationship('Restaurant', back_populates='manager', uselist=False)

    # Password methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # String representation
    def __repr__(self):
        return f"<User {self.email}>"



class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=True) # Nullable for now
    longitude = db.Column(db.Float, nullable=True) # Nullable for now
    
    # Relationships
    categories = db.relationship(
        'Category',
        secondary=restaurant_categories,
        back_populates='restaurants'
    )
    reservations = db.relationship('Reservation', back_populates='restaurant', cascade='all, delete-orphan')
    manager = db.relationship('User', back_populates='restaurant', uselist=False)
    
    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relationship to Restaurant
    restaurants = db.relationship(
        'Restaurant',
        secondary=restaurant_categories,
        back_populates='categories'
    )
    
    def __repr__(self):
        return f"<Category {self.name}>"



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


