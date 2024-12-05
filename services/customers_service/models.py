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



