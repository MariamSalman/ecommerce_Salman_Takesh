from database import db

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    email = db.Column(db.String(120), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)
    wallet_balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

"""
The `Customer` class represents a customer in the system, and is used for interacting with the `customers` table in the database.

Attributes:
- `id` (int): The unique identifier for the customer (Primary Key).
- `full_name` (str): The full name of the customer.
- `username` (str): The unique username chosen by the customer (unique).
- `password` (str): The hashed password of the customer for secure authentication.
- `email` (str): The unique email address of the customer (unique).
- `age` (int): The age of the customer (optional).
- `address` (str): The address of the customer (optional).
- `gender` (str): The gender of the customer (optional).
- `marital_status` (str): The marital status of the customer (optional).
- `wallet_balance` (float): The wallet balance of the customer (defaults to 0.0).
- `created_at` (datetime): The timestamp when the customer account was created (automatically set to the current time).

Methods:
- As a model for SQLAlchemy, the `Customer` class inherits from `db.Model`, which provides all the CRUD operations (Create, Read, Update, Delete) for interacting with the `customers` table in the database.
- The class is mapped to the `customers` table in the database, and its columns correspond to the attributes defined in the class.

Usage:
- The class can be used to create, query, update, and delete customer records in the database.
- It provides a structured way to store customer information, such as authentication details and personal data.
"""
