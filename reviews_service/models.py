from database import db

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="pending")  # approved, flagged, pending