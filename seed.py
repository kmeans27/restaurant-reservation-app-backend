# seed.py

from app import create_app, db
from app.models import FrontendUser, User, Reservation, Restaurant, Category
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import random

app = create_app()

# initialize geolocator
geolocator = Nominatim(user_agent="restaurant_reservation_app")

def geocode_address(address, max_retries=3):
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            else:
                return (None, None)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            app.logger.error(f"Geocoding error for address '{address}': {e}")
            time.sleep(1)  # Wait before retrying
    return (None, None)

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
    # ---------------------------
    # 2. Create Restaurants with Updated Locations and Geocoding
    # ---------------------------
        restaurants = [
            {
                'name': 'Luigi’s Italian Bistro',
                'address': 'Via Madonna del Suffragio, 17, 39011 Lana BZ, Italy',
                'phone_number': '0123456789',
                'description': 'Authentic Italian cuisine with a modern twist.',
                'manager_id': 1,  # Ensure this manager exists
                'categories': [categories[0], categories[19]] # Italian
            },
            {
                'name': 'Dragon Palace',
                'address': 'Via Argentieri, 16, 39100 Bolzano BZ, Italy',
                'phone_number': '0123456789',
                'description': 'Traditional Chinese dishes served in a cozy environment.',
                'manager_id': 2,  # Ensure this manager exists
                'categories': [categories[1], categories[16]]   # Chinese
            },
            {
                'name': 'El Taco Loco',
                'address': 'Via del Laghetto, 17, 39042 Bressanone BZ, Italy',
                'phone_number': '0123456789',
                'description': 'A vibrant spot for the best tacos and margaritas.',
                'manager_id': 3,  # Ensure this manager exists
                'categories': [categories[2], categories[17]] # Mexican
            },
            # Add more restaurants as needed
        ]

        for r in restaurants:
            lat, lon = geocode_address(r['address'])
            restaurant = Restaurant(
                name=r['name'],
                address=r['address'],
                phone_number=r['phone_number'],
                description=r['description'],
                manager_id=r['manager_id'],
                categories=r['categories'],
                latitude=lat,
                longitude=lon
            )
            db.session.add(restaurant)
            # Optional: Log if geocoding was unsuccessful
            if lat is None or lon is None:
                app.logger.warning(f"Geocoding failed for restaurant '{r['name']}' at address '{r['address']}'.")

        db.session.commit()

            # ---------------------------
        # 3. Create FrontendUsers
        # ---------------------------
        frontend_users = [
            FrontendUser(
                user_id='user_001',
                email='john.doe@example.com',      # Nullable for now
                password=None,                     # Nullable for now
                name=None                          # Nullable for now
            ),
            FrontendUser(
                user_id='user_002',
                email='jane.smith@example.com',
                password=None,
                name=None
            ),
            FrontendUser(
                user_id='user_003',
                email='alice.wonder@example.com',
                password=None,
                name=None
            ),
            # Add more frontend users as needed
        ]

        db.session.add_all(frontend_users)
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
                status='pending',
                frontend_user_id= frontend_users[0].id  # Add the frontend user ID here
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
                status='pending',
                frontend_user_id= frontend_users[1].id  # Add the frontend user ID here
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
                status='pending',
                frontend_user_id= frontend_users[2].id  # Add the frontend user ID here

            )
            db.session.add(reservation)
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
