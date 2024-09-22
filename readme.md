# Restaurant Reservation App

![Restaurant Reservation App]

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [API Documentation](#api-documentation)
  - [Restaurants Endpoints](#restaurants-endpoints)
  - [Categories Endpoints](#categories-endpoints)
  - [Reservations Endpoints](#reservations-endpoints)
- [Next Steps](#next-steps)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Overview

The **Restaurant Reservation App** is a web-based platform designed to streamline the process of managing restaurant information and handling customer reservations. Built with Flask, this application allows restaurant managers to create and edit restaurant profiles, assign multiple categories to each restaurant, and manage reservations through a robust API.

## Features

- **Restaurant Management:**
  - **Create Restaurants:** Add new restaurants with details such as name, address, phone number, description, and assign multiple categories.
  - **Edit Restaurants:** Update existing restaurant information and manage associated categories.
  - **List Restaurants:** View a comprehensive list of all registered restaurants along with their categories.

- **Category Management:**
  - **View Categories:** Retrieve a list of all available restaurant categories.
  - **Filter Restaurants by Category:** Display restaurants filtered by selected categories.

- **Reservation Management:**
  - **Create Reservations:** Allow customers to create reservations by specifying restaurant, date, time, number of people, and personal details.
  - **Update Reservation Status:** Enable restaurant managers to accept or decline reservations.
  - **List Reservations:** View all reservations associated with a particular restaurant.

- **API Endpoints:**
  - Comprehensive API endpoints for interacting with restaurants, categories, and reservations.
  - Example usage with `curl` commands provided for easy integration.

- **User-Friendly Interface:**
  - Intuitive frontend templates for managing restaurants and reservations.
  - Responsive design for optimal viewing on various devices.

## Technology Stack

- **Backend:**
  - [Flask](https://flask.palletsprojects.com/) - Web framework for Python.
  - [Flask-WTF](https://flask-wtf.readthedocs.io/) - Form handling and CSRF protection.
  - [SQLAlchemy](https://www.sqlalchemy.org/) - ORM for database interactions.
  - [SQLite](https://www.sqlite.org/index.html) - Lightweight relational database.

- **Frontend:**
  - HTML5 & CSS3 - Markup and styling.
  - JavaScript - Client-side interactivity.

- **Version Control:**
  - [Git](https://git-scm.com/) - Version control system.
  - [GitHub](https://github.com/) - Hosting for version control and collaboration.

## API Documentation
### Restaurants Endpoints
- **GET /api/restaurants**
    - Retrieve a list of all restaurants with their associated categories
    - curl http://localhost:5000/api/restaurants

- **GET /api/restaurants/<int:restaurant_id>**
    - Retrieve detailed information about a specific restaurant, including categories and reservations.
    - curl http://localhost:5000/api/restaurants/1

### Categories Endpoints

- **GET /api/categories**
    - Retrieve a list of all restaurant categories.
    - curl http://localhost:5000/api/categories

- **GET /api/categories/<int:category_id>/restaurants**
    - Retrieve a list of restaurants filtered by a specific category.
    - curl http://localhost:5000/api/categories/1/restaurants

### Reservations Endpoints

- **POST /api/reservations**
    - Create a new reservation
    - curl -X POST http://localhost:5000/api/reservations \
    -H "Content-Type: application/json" \
    -d '{
        "restaurant_id": 1,
        "name": "Max Mustermann",
        "date": "2024-05-20",
        "time": "19:30",
        "number_of_people": 4,
        "timestamp": "2024-04-27T14:35:22Z"
    }'

- **POST /api/reservations/<int:reservation_id>**
    - Update the status of a reservation (accept or decline).
    - curl -X PATCH http://localhost:5000/api/reservations/1 \
    -H "Content-Type: application/json" \
    -d '{
        "status": "accepted"
    }'


## Next Steps

1. Create a new API Endpoint to send reservation data to the Frontend APP
2. Define an unique identifier for the frontend user so we can differentiate between their information/reservations
3. Create a login functionality and a way to sign up
4. Create a Dashboard where the Restaurant sees their most important information clearly