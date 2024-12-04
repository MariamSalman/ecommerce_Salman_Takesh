from app import app
from models import db, Good

with app.app_context():
    db.session.add(Good(name="Laptop", category="electronics", price=1500.0, stock_count=10))
    db.session.add(Good(name="Headphones", category="electronics", price=200.0, stock_count=15))
    db.session.commit()
    print("Database initialized with sample data.")
