from database import db

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    good_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="pending")  # approved, flagged, pending

"""
The `Review` class represents a review for a product (good) in the system and is used to interact with the `reviews` table in the database.

Attributes:
- `id` (int): The unique identifier for the review (Primary Key).
- `good_id` (int): The ID of the product being reviewed (Foreign Key).
- `username` (str): The username of the person who submitted the review (required).
- `rating` (int): The rating provided by the user (required).
- `comment` (str): The text of the review comment (required).
- `status` (str): The status of the review (default: "pending"). This could be "approved", "flagged", or "pending".

Methods:
- As a model for SQLAlchemy, the `Review` class inherits from `db.Model`, which provides all the necessary CRUD operations (Create, Read, Update, Delete) for interacting with the `reviews` table in the database.

Usage:
- The `Review` class is used to define the structure of a product review in the database.
- It can be used to create new reviews, query existing reviews, update review details, and manage the status of reviews.

Example:
    - `Review.query.filter_by(good_id=1).all()` retrieves all reviews for the product with ID 1.
    - `db.session.add(new_review)` adds a new review to the database.
    - `db.session.commit()` commits the changes to the database.

The `Review` model helps manage user feedback, including the product rating, review comments, and the review's approval status.
"""
