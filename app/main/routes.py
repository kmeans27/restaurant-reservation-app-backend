# app/main/routes.py

from flask import render_template, redirect, url_for, request, flash, jsonify, abort, current_app
from app.main import bp
from app.models import Restaurant, Reservation, Category, FrontendUser, User
from app import db
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest
from app.main.forms import RestaurantForm
from sqlalchemy.exc import SQLAlchemyError
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
from flask_login import login_required, current_user 

# Initialize the Geocoder
geolocator = Nominatim(user_agent="restaurant_reservation_app")
# Define Helper Function for Geocoding
def geocode_address(address, max_retries=3):
    for attempt in range(max_retries):
        try:
            location = geolocator.geocode(address)
            if location:
                return (location.latitude, location.longitude)
            else:
                return (None, None)
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            current_app.logger.error(f"Geocoding error for address '{address}': {e}")
            time.sleep(1)  # Wait before retrying
    return (None, None)



# HTML Routes

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/restaurants')
def list_restaurants():
    restaurants = Restaurant.query.all()
    return render_template('restaurants.html', restaurants=restaurants)

@bp.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('restaurant_detail.html', restaurant=restaurant)


@bp.route('/reservations')
def list_reservations():
    reservations = Reservation.query.all()
    return render_template('reservations.html', reservations=reservations)

@bp.route('/restaurants/create', methods=['GET', 'POST'])
#UPDATED create_restaurant function to handle user creation
def create_restaurant():
    form = RestaurantForm()
    
    if form.validate_on_submit():
        # Extract form data
        name = form.name.data
        address = form.address.data
        phone_number = form.phone_number.data
        description = form.description.data
        category_ids = form.categories.data
        email = form.email.data
        password = form.password.data

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('create_restaurant.html', form=form)

        # Create User
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Flush to assign an ID

        # Fetch selected categories
        selected_categories = Category.query.filter(Category.id.in_(category_ids)).all()

        # Geocode the address
        lat, lon = geocode_address(address)
        if lat is None or lon is None:
            flash('Unable to geocode the address. Please ensure it is correct.', 'danger')
            db.session.rollback()
            return render_template('create_restaurant.html', form=form)
        
        # Create Restaurant and associate with User
        restaurant = Restaurant(
            name=name,
            address=address,
            phone_number=phone_number,
            description=description,
            manager=user,  # Associate with User
            categories=selected_categories,
            latitude=lat,
            longitude=lon
        )

        db.session.add(restaurant)
        db.session.commit()

        flash('Restaurant and user account created successfully!', 'success')
        return redirect(url_for('main.list_restaurants'))
    
    else:
        if request.method == 'POST':
            flash('Please correct the errors in the form.', 'danger')
    
    return render_template('create_restaurant.html', form=form)

@bp.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    form = RestaurantForm(obj=restaurant)  # Populate form with restaurant data
    # Set category choices
    form.categories.choices = [(category.id, category.name) for category in Category.query.all()]
    
    if form.validate_on_submit():
        # Update restaurant attributes from form data
        restaurant.name = form.name.data
        restaurant.address = form.address.data
        restaurant.phone_number = form.phone_number.data
        restaurant.description = form.description.data
        
        # Update categories
        selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
        restaurant.categories = selected_categories
        
        db.session.commit()
        flash('Restaurant updated successfully!', 'success')
        return redirect(url_for('main.get_restaurant_detail', restaurant_id=restaurant.id))
    else:
        if request.method == 'POST':
            flash('Please correct the errors in the form.', 'error')
    
    # Pre-select current categories
    form.categories.data = [category.id for category in restaurant.categories]
    
    return render_template('edit_restaurant.html', form=form, restaurant=restaurant)



@bp.route('/restaurants/manage')
def manage_restaurants():
    # For now, we'll just list all restaurants
    restaurants = Restaurant.query.all()
    return render_template('manage_restaurants.html', restaurants=restaurants)

# Reservation management routes
# HTML Route to manage reservations for a specific restaurant
@bp.route('/restaurants/<int:restaurant_id>/reservations', methods=['GET', 'POST'])
def manage_reservations(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    # Fetch upcoming reservations (reservation_datetime >= now)
    now = datetime.now()
    reservations = Reservation.query.filter(
        Reservation.restaurant_id == restaurant_id,
        Reservation.reservation_datetime >= now,
        Reservation.status.in_(['pending', 'accepted', 'declined'])
    ).order_by(Reservation.reservation_datetime.asc()).all()
    
    return render_template('manage_reservations.html', restaurant=restaurant, reservations=reservations)


# HTML Route to update reservation status
@bp.route('/api/reservations/<int:reservation_id>/status', methods=['POST'])
def update_reservation_status(reservation_id):
    # Determine the request type
    if request.is_json:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Missing required fields.'}), 400
        new_status = data.get('status')
    else:
        # Assume form data
        new_status = request.form.get('status')
        if not new_status:
            return jsonify({'error': 'Missing required fields.'}), 400

    if new_status not in ['accepted', 'declined']:
        return jsonify({'error': 'Invalid status value.'}), 400

    try:
        reservation = Reservation.query.get_or_404(reservation_id)

        # Update status
        reservation.status = new_status

        db.session.commit()
        return jsonify({'message': f'Reservation {new_status} successfully.'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error: {str(e)}")
        return jsonify({'error': 'An error occurred while updating the reservation.'}), 500


# API ENDPOINTS

@bp.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    data = []
    for restaurant in restaurants:
        data.append({
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'phoneNumber': restaurant.phone_number,  # Changed to camelCase
            'description': restaurant.description,
            'latitude': restaurant.latitude,        # Added latitude
            'longitude': restaurant.longitude, 
            'categories': [category.name for category in restaurant.categories]
        })
    return jsonify(data)

@bp.route('/api/restaurants/<int:restaurant_id>', methods=['GET'], endpoint='api_get_restaurant')
def api_get_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    data = {
        'id': restaurant.id,
        'name': restaurant.name,
        'address': restaurant.address,
        'phoneNumber': restaurant.phone_number,  # Changed to camelCase
        'description': restaurant.description,
        'latitude': restaurant.latitude,        # Added latitude
        'longitude': restaurant.longitude,      # Added longitude
        'categories': [category.name for category in restaurant.categories],
        'reservations': [
            {
                'id': reservation.id,
                'reservationDatetime': reservation.reservation_datetime.isoformat(),
                'personCount': reservation.person_count,  # Corrected attribute
                'status': reservation.status,
                'name': reservation.name  # Replaced 'userId' with 'name'
            }
            for reservation in restaurant.reservations
        ]
    }
    
    return jsonify(data)



@bp.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    data = [{'id': category.id, 'name': category.name} for category in categories]
    return jsonify(data)

@bp.route('/api/categories/<int:category_id>/restaurants', methods=['GET'])
def get_restaurants_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    restaurants = category.restaurants
    data = []
    for restaurant in restaurants:
        data.append({
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'phoneNumber': restaurant.phone_number,  # Changed to camelCase
            'description': restaurant.description,
            'categories': [cat.name for cat in restaurant.categories]
            # Optionally, include reservations if needed
        })
    return jsonify(data)

@bp.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data.'}), 400

    # Extract data using new variable names
    restaurant_id = data.get('restaurant_id')
    name = data.get('name')
    date_str = data.get('date')
    time_str = data.get('time')
    number_of_people = data.get('number_of_people')
    timestamp_str = data.get('timestamp')
    user_id = data.get('user_id')  # Extract the userId from the frontend

    # Validate required fields
    if not all([restaurant_id, name, date_str, time_str, number_of_people, timestamp_str, user_id]):
        return jsonify({'error': 'Missing required fields.'}), 400

    # Validate restaurant existence
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found.'}), 404

    try:
        # Combine date and time into a single datetime object
        reservation_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        return jsonify({'error': 'Invalid date or time format.'}), 400

    try:
        # Parse timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid timestamp format.'}), 400

    # Handle FrontendUser
    frontend_user = FrontendUser.query.filter_by(user_id=user_id).first()
    if not frontend_user:
        # Create a new FrontendUser if it doesn't exist
        frontend_user = FrontendUser(user_id=user_id)
        db.session.add(frontend_user)
        db.session.flush()  # Flush to get the frontend_user.id

    # Create a new Reservation object
    new_reservation = Reservation(
        restaurant_id=restaurant_id,
        name=name,
        reservation_datetime=reservation_datetime,
        person_count=number_of_people,
        timestamp=timestamp,
        status='pending',  # Assuming default status
        frontend_user=frontend_user  # Associate the reservation with the FrontendUser
    )

    db.session.add(new_reservation)
    db.session.commit()

    return jsonify({'message': 'Reservation created successfully.', 'reservation_id': new_reservation.id}), 201


# Endpoint to update reservation status (accept or decline)
@bp.route('/api/reservations/<int:reservation_id>', methods=['PATCH'])
def update_reservation(reservation_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON data.'}), 400

    status = data.get('status')  # Assuming 'status' remains unchanged

    if status not in ['accepted', 'declined']:
        return jsonify({'error': 'Invalid status value.'}), 400

    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({'error': 'Reservation not found.'}), 404

    reservation.status = status
    db.session.commit()

    return jsonify({'message': f'Reservation {status} successfully.'}), 200

# retrieve all reservations for a specific user_id (frontend)
@bp.route('/api/users/<string:user_id>/reservations', methods=['GET'])
def get_user_reservations(user_id):
    frontend_user = FrontendUser.query.filter_by(user_id=user_id).first()
    if not frontend_user:
        return jsonify({'error': 'User not found.'}), 404

    reservations = frontend_user.reservations
    reservations_data = []
    for reservation in reservations:
        reservations_data.append({
            'reservation_id': reservation.id,
            'restaurant_id': reservation.restaurant_id,
            'restaurant_name': reservation.restaurant.name,
            'reservation_datetime': reservation.reservation_datetime.isoformat(),
            'person_count': reservation.person_count,
            'status': reservation.status,
            'name': reservation.name
        })

    return jsonify({'reservations': reservations_data}), 200






@bp.route('/dashboard')
@login_required
def dashboard():
    # Get the user's restaurant
    user_restaurant = current_user.restaurant

    if not user_restaurant:
        flash('You do not have a restaurant associated with your account.', 'warning')
        return redirect(url_for('main.create_restaurant'))

    # Get reservations for the user's restaurant
    reservations = Reservation.query.filter_by(restaurant_id=user_restaurant.id).filter(
        Reservation.reservation_datetime >= datetime.utcnow()
    ).order_by(Reservation.reservation_datetime).limit(5).all()

    # Prepare data for the chart
    # Example: Count reservations by hour
    from collections import Counter
    import json

    # Filter reservations based on the selected time frame (e.g., today)
    time_frame = request.args.get('time_frame', 'today')
    if time_frame == 'today':
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=1)
    elif time_frame == 'week':
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(weeks=1)
    elif time_frame == 'month':
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=30)
    else:
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=1)

    # Get reservations in the time frame
    chart_reservations = Reservation.query.filter_by(restaurant_id=user_restaurant.id).filter(
        Reservation.reservation_datetime >= start_date,
        Reservation.reservation_datetime < end_date
    ).all()

    # Count reservations by hour
    reservation_hours = [res.reservation_datetime.hour for res in chart_reservations]
    hour_counts = Counter(reservation_hours)
    hours = list(range(24))
    counts = [hour_counts.get(hour, 0) for hour in hours]

    return render_template(
        'dashboard.html',
        reservations=reservations,
        hours=json.dumps(hours),
        counts=json.dumps(counts),
        time_frame=time_frame
    )


@bp.route('/my_reservations')
@login_required
def my_reservations():
    # Get the user's restaurant
    user_restaurant = current_user.restaurant

    if not user_restaurant:
        flash('You do not have a restaurant associated with your account.', 'warning')
        return redirect(url_for('main.create_restaurant'))

    # Get reservations for the user's restaurant
    reservations = Reservation.query.filter_by(restaurant_id=user_restaurant.id).order_by(
        Reservation.reservation_datetime.desc()
    ).all()

    return render_template('manage_reservations.html', reservations=reservations, restaurant=user_restaurant)

