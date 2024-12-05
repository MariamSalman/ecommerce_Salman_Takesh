from database import db

class Good(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock_count = db.Column(db.Integer, nullable=False)

"""
The `Good` class represents a product in the system and is used to interact with the `goods` table in the database.

Attributes:
- `id` (int): The unique identifier for the good (Primary Key).
- `name` (str): The name of the product (required).
- `category` (str): The category of the product (required).
- `price` (float): The price of the product (required).
- `description` (str): A description of the product (optional).
- `stock_count` (int): The number of items available in stock (required).

Methods:
- As a model for SQLAlchemy, the `Good` class inherits from `db.Model`, which provides all the necessary CRUD operations (Create, Read, Update, Delete) for interacting with the `goods` table in the database.

Usage:
- The `Good` class is used to define the structure of a product in the database.
- It can be used to create new goods, query existing goods, update product details, and manage inventory.

Example:
    - `Good.query.filter_by(name="Product Name").first()` retrieves the first product with the name "Product Name" from the database.
    - `db.session.add(new_good)` adds a new product to the database.
    - `db.session.commit()` commits the changes to the database.

The `Good` model is used for managing product information, such as pricing, description, and inventory tracking.
"""
