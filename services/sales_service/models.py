from database import db
from datetime import datetime

class Good(db.Model):
    """
    Represents a product in the inventory.

    The `Good` model is used to define the products that are available for sale. It contains information about 
    the product such as name, category, price, and stock count.

    Attributes:
        id (int): The unique identifier for the product (Primary Key).
        name (str): The name of the product.
        category (str): The category of the product (e.g., electronics, apparel).
        price (float): The price of the product.
        stock_count (int): The number of items available in stock.
    
    Methods:
        None (this is just a model representation of a product)
    """
    __tablename__ = 'goods'

    id = db.Column(db.Integer, primary_key=True)  # Unique product identifier
    name = db.Column(db.String(80), nullable=False)  # Name of the product
    category = db.Column(db.String(50), nullable=False)  # Category of the product (e.g., electronics)
    price = db.Column(db.Float, nullable=False)  # Price of the product
    stock_count = db.Column(db.Integer, nullable=False)  # Number of items in stock

class Sale(db.Model):
    """
    Represents a sale transaction.

    The `Sale` model tracks the sale of goods by storing the sale details, including 
    the product sold, the username of the customer, the quantity sold, and the timestamp of the sale.

    Attributes:
        id (int): The unique identifier for the sale transaction (Primary Key).
        good_id (int): The `id` of the product sold (Foreign Key to `Good` model).
        username (str): The username of the customer who made the purchase.
        quantity (int): The number of items purchased in this transaction.
        timestamp (datetime): The timestamp when the sale occurred (defaults to current time).
    
    Methods:
        None (this is just a model representation of a sale transaction)
    """
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)  # Unique sale transaction identifier
    good_id = db.Column(db.Integer, nullable=False)  # ID of the product sold (linked to `Good`)
    username = db.Column(db.String(80), nullable=False)  # Username of the customer
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of products sold
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of when the sale occurred (default to current time)
