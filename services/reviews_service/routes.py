from flask_restful import Api, Resource
from models import Review
from database import db
from flask import request, jsonify

api = Api()

class SubmitReview(Resource):
    def post(self):
        data = request.json
        good_id = data.get('good_id')
        username = data.get('username')
        rating = data.get('rating')
        comment = data.get('comment')

        if not (1 <= rating <= 5):
            return {"error": "Rating must be between 1 and 5"}, 400

        review = Review(
            good_id=good_id,
            username=username,
            rating=rating,
            comment=comment,
        )
        db.session.add(review)
        db.session.commit()
        return {"message": "Review submitted successfully"}, 201

class GetProductReviews(Resource):
    def get(self, good_id):
        reviews = Review.query.filter_by(good_id=good_id).all()
        return jsonify([{
            'id': review.id,
            'username': review.username,
            'rating': review.rating,
            'comment': review.comment,
            'status': review.status
        } for review in reviews])

class ModerateReview(Resource):
    def put(self, review_id):
        data = request.json
        status = data.get('status')
        if status not in ["approved", "flagged"]:
            return {"error": "Invalid status"}, 400

        review = Review.query.get(review_id)
        if not review:
            return {"error": "Review not found"}, 404

        review.status = status
        db.session.commit()
        return {"message": "Review status updated successfully"}, 200

api.add_resource(SubmitReview, '/reviews/<int:good_id>')
api.add_resource(GetProductReviews, '/reviews/product/<int:good_id>')
api.add_resource(ModerateReview, '/reviews/moderate/<int:review_id>')
