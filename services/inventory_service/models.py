from database import db

class Good(db.Model):
    __tablename__ = 'goods'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    stock_count = db.Column(db.Integer, nullable=False)
