from app import app
from models import db, Good

with app.app_context():
    db.session.add(Good(name="Laptop", category="electronics", price=10.0, stock_count=10))
    db.session.add(Good(name="Headphones", category="electronics", price=200.0, stock_count=15))
    db.session.commit()
    print("Database initialized with sample data.")

"""
This script initializes the database with sample data for testing purposes.

- The script runs within the Flask application context (`app.app_context()`), ensuring that database operations are performed within the application's lifecycle.
- It adds two sample products to the `Good` table in the database:

  1. **Laptop**: An electronic item with a price of $10.0 and 10 items in stock.
  2. **Headphones**: An electronic item with a price of $200.0 and 15 items in stock.

Steps:
1. **Initialize App Context**: The `with app.app_context()` block ensures that the database session is tied to the current Flask application context. This is essential for interacting with the database within Flask.
2. **Add Sample Data**: Using `db.session.add()`, two `Good` objects are added to the session.
3. **Commit Changes**: The changes are committed to the database using `db.session.commit()`.
4. **Log Success**: A message is printed to indicate that the database has been initialized with sample data.

Usage:
- Run this script to populate the `Good` table with initial data for testing or development.
- This script should be executed only during development or when needing to reset the database with sample entries.
"""

