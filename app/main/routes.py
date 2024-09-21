# app/main/routes.py

from flask import render_template, redirect, url_for, request, flash, jsonify, abort
from app.main import bp
from app.models import Restaurant, Reservation, Category
from app import db
from datetime import datetime
from werkzeug.exceptions import BadRequest
from app.main.forms import RestaurantForm



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
def create_restaurant():
    form = RestaurantForm()
    # Populate category choices
    form.categories.choices = [(category.id, category.name) for category in Category.query.all()]
    
    if request.method == 'GET':
        form.categories.data = []  # Initialize to empty list to prevent 'NoneType' errors
    
    if form.validate_on_submit():
        name = form.name.data
        address = form.address.data
        phone_number = form.phone_number.data
        description = form.description.data
        manager_id = 1  # Assign to a default manager or handle appropriately
    
        # Fetch selected Category objects
        selected_categories = Category.query.filter(Category.id.in_(form.categories.data)).all()
    
        # Create a new Restaurant object with selected categories
        new_restaurant = Restaurant(
            name=name,
            address=address,
            phone_number=phone_number,
            description=description,
            manager_id=manager_id,
            categories=selected_categories
        )
        db.session.add(new_restaurant)
        db.session.commit()
        flash('Restaurant created successfully!', 'success')
        return redirect(url_for('main.list_restaurants'))
    else:
        if request.method == 'POST':
            flash('Please correct the errors in the form.', 'error')
    
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
def update_reservation_status_html(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    
    status = request.form.get('status')
    if status not in ['accepted', 'declined']:
        flash('Invalid status update.', 'error')
        return redirect(url_for('main.manage_reservations', restaurant_id=reservation.restaurant_id))
    
    if reservation.status != 'pending':
        flash('Only pending reservations can be updated.', 'error')
        return redirect(url_for('main.manage_reservations', restaurant_id=reservation.restaurant_id))
    
    reservation.status = status
    db.session.commit()
    flash(f'Reservation {status} successfully.', 'success')
    
    return redirect(url_for('main.manage_reservations', restaurant_id=reservation.restaurant_id))


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


# Endpoint to create a new reservation
@bp.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    # Extract and validate data
    reservation_datetime_str = data.get('reservationDatetime')
    name = data.get('name')
    person_count = data.get('personCount')
    restaurant_id = data.get('restaurantId')
    
    if not all([reservation_datetime_str, name, person_count, restaurant_id]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Parse reservation_datetime
        reservation_datetime = datetime.strptime(reservation_datetime_str, '%d/%m/%Y %H:%M')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use DD/MM/YYYY HH:MM'}), 400
    
    # Optional: Validate restaurant existence
    restaurant = Restaurant.query.get(restaurant_id)
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Create Reservation object
    reservation = Reservation(
        reservation_datetime=reservation_datetime,
        name=name,
        person_count=person_count,
        restaurant_id=restaurant_id,
        status='pending'  # Default status
    )
    
    # Add to database
    db.session.add(reservation)
    db.session.commit()
    
    return jsonify({'message': 'Reservation created successfully', 'reservation_id': reservation.id}), 201

# Endpoint to update reservation status (accept or decline)
@bp.route('/api/reservations/<int:reservation_id>', methods=['PATCH'])
def update_reservation_status(reservation_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400
    
    status = data.get('status')
    if status not in ['accepted', 'declined']:
        return jsonify({'error': 'Invalid status. Must be "accepted" or "declined"'}), 400
    
    reservation = Reservation.query.get_or_404(reservation_id)
    
    # Only allow updating if status is pending
    if reservation.status != 'pending':
        return jsonify({'error': 'Only pending reservations can be updated'}), 400
    
    reservation.status = status
    db.session.commit()
    
    return jsonify({'message': f'Reservation {status} successfully'}), 200
