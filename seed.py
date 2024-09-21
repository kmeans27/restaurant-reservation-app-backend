# seed.py

from app import create_app, db
from app.models import Restaurant, Category, Reservation
from datetime import datetime, timedelta
import random

app = create_app()

def seed():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Create Categories
        categories = [
            Category(name='Italian'),
            Category(name='Chinese'),
            Category(name='Mexican'),
            Category(name='Indian'),
            Category(name='Japanese'),
            Category(name='French'),
            Category(name='Thai'),
            Category(name='American'),
            Category(name='Mediterranean'),
            Category(name='Vegetarian'),
            Category(name='Seafood'),
            Category(name='Steakhouse'),
            Category(name='Vegan'),
            Category(name='BBQ'),
            Category(name='Bakery'),
            Category(name='Cafe'),
            Category(name='Bar'),
            Category(name='Dessert'),
            Category(name='Fusion'),
            Category(name='Buffet')
        ]
        db.session.add_all(categories)
        db.session.commit()
        
        # Create Restaurants
        restaurants = [
            Restaurant(
                name='Luigi’s Italian Bistro',
                address='123 Pasta Lane',
                phone_number='555-1234',
                description='Authentic Italian cuisine with a modern twist.',
                manager_id=1,
                categories=[categories[0], categories[19]]  # Italian, Buffet
            ),
            Restaurant(
                name='Dragon Palace',
                address='456 Noodle Street',
                phone_number='555-5678',
                description='Traditional Chinese dishes served in a cozy environment.',
                manager_id=2,
                categories=[categories[1], categories[16]]  # Chinese, Bar
            ),
            Restaurant(
                name='El Taco Loco',
                address='789 Fiesta Avenue',
                phone_number='555-9012',
                description='Spicy Mexican food that will ignite your taste buds.',
                manager_id=3,
                categories=[categories[2], categories[17]]  # Mexican, Dessert
            ),
            # Add more restaurants as needed
        ]
        db.session.add_all(restaurants)
        db.session.commit()
        
        # Create Reservations
        # Generate reservations for the first restaurant
        for i in range(1, 6):
            reservation_datetime = datetime.now() + timedelta(days=random.randint(1, 10), hours=random.randint(0, 23))
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
            reservation = Reservation(
                reservation_datetime=reservation_datetime,
                timestamp=timestamp,
                person_count=random.randint(1, 6),
                restaurant_id=1,
                name=f'Customer {i}',
                status='pending'
            )
            db.session.add(reservation)
        
        # Generate reservations for the second restaurant
        for i in range(6, 11):
            reservation_datetime = datetime.now() + timedelta(days=random.randint(1, 10), hours=random.randint(0, 23))
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
            reservation = Reservation(
                reservation_datetime=reservation_datetime,
                timestamp=timestamp,
                person_count=random.randint(1, 6),
                restaurant_id=2,
                name=f'Customer {i}',
                status='pending'
            )
            db.session.add(reservation)
        
        # Generate reservations for the third restaurant
        for i in range(11, 16):
            reservation_datetime = datetime.now() + timedelta(days=random.randint(1, 10), hours=random.randint(0, 23))
            timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
            reservation = Reservation(
                reservation_datetime=reservation_datetime,
                timestamp=timestamp,
                person_count=random.randint(1, 6),
                restaurant_id=3,
                name=f'Customer {i}',
                status='pending'
            )
            db.session.add(reservation)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
