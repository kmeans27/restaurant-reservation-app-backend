# app/main/routes.py
from flask import render_template, redirect, url_for, request, flash, jsonify
from app.main import bp
from app.models import Restaurant, Reservation
from app import db

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/restaurants')
def list_restaurants():
    restaurants = Restaurant.query.all()
    return render_template('restaurants.html', restaurants=restaurants)

@bp.route('/restaurants/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('restaurant_detail.html', restaurant=restaurant)

@bp.route('/reservations')
def list_reservations():
    reservations = Reservation.query.all()
    return render_template('reservations.html', reservations=reservations)


@bp.route('/restaurants/create', methods=['GET', 'POST'])
def create_restaurant():
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        description = request.form.get('description')
        manager_id = 1  # For simplicity, assign to a default manager
        
        # Create a new Restaurant object
        new_restaurant = Restaurant(
            name=name,
            address=address,
            phone_number=phone_number,
            description=description,
            manager_id=manager_id
        )
        db.session.add(new_restaurant)
        db.session.commit()
        flash('Restaurant created successfully!')
        return redirect(url_for('main.list_restaurants'))
    return render_template('create_restaurant.html')

@bp.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    if request.method == 'POST':
        restaurant.name = request.form.get('name')
        restaurant.address = request.form.get('address')
        restaurant.phone_number = request.form.get('phone_number')
        restaurant.description = request.form.get('description')
        
        db.session.commit()
        flash('Restaurant updated successfully!')
        return redirect(url_for('main.restaurant_detail', restaurant_id=restaurant.id))
    return render_template('edit_restaurant.html', restaurant=restaurant)

@bp.route('/restaurants/manage')
def manage_restaurants():
    # For now, we'll just list all restaurants
    restaurants = Restaurant.query.all()
    return render_template('manage_restaurants.html', restaurants=restaurants)


# API ENDPOINTS
@bp.route('/api/restaurants', methods=['GET'])
def api_get_restaurants():
    restaurants = Restaurant.query.all()
    data = []
    for r in restaurants:
        data.append({
            'id': r.id,
            'name': r.name,
            'address': r.address,
            'phone_number': r.phone_number,
            'description': r.description,
        })
    return jsonify(data)