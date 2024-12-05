from flask_restful import Api, Resource
from models import Review
from database import db
from flask import request, jsonify
from utils import log_to_audit, encrypt_data, decrypt_data, circuit_breaker
from flask_limiter import Limiter

api = Api()


class SubmitReview(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @circuit_breaker
    def post(self):
        data = request.json
        good_id = data.get('good_id')
        username = data.get('username')
        rating = data.get('rating')
        comment = data.get('comment')

        if not good_id or not username or not rating or not comment:
            log_to_audit("reviews_service", "/reviews", "error", "Missing required fields")
            return {"error": "All fields (good_id, username, rating, comment) are required"}, 400

        if not (1 <= rating <= 5):
            log_to_audit("reviews_service", "/reviews", "error", "Invalid rating value")
            return {"error": "Rating must be between 1 and 5"}, 400

        encrypted_comment = encrypt_data(comment)
        review = Review(good_id=good_id, username=username, rating=rating, comment=encrypted_comment)
        db.session.add(review)
        db.session.commit()

        log_to_audit("reviews_service", "/reviews", "success", f"Review submitted for good_id {good_id} by {username}")
        return {"message": "Review submitted successfully"}, 201


class UpdateReview(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def put(self, review_id):
        data = request.json
        review = Review.query.get(review_id)
        if not review:
            log_to_audit("reviews_service", f"/reviews/{review_id}", "error", "Review not found")
            return {"error": "Review not found"}, 404

        if "rating" in data:
            if not (1 <= data['rating'] <= 5):
                return {"error": "Rating must be between 1 and 5"}, 400
            review.rating = data['rating']

        if "comment" in data:
            review.comment = encrypt_data(data['comment'])

        db.session.commit()
        log_to_audit("reviews_service", f"/reviews/{review_id}", "success", f"Review {review_id} updated")
        return {"message": "Review updated successfully"}, 200


class DeleteReview(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def delete(self, review_id):
        review = Review.query.get(review_id)
        if not review:
            log_to_audit("reviews_service", f"/reviews/{review_id}", "error", "Review not found")
            return {"error": "Review not found"}, 404

        db.session.delete(review)
        db.session.commit()
        log_to_audit("reviews_service", f"/reviews/{review_id}", "success", f"Review {review_id} deleted")
        return {"message": "Review deleted successfully"}, 200


class GetProductReviews(Resource):
    decorators = [limiter.limit("20/minute")]  # Limit this endpoint to 20 requests per minute

    @circuit_breaker
    def get(self, good_id):
        reviews = Review.query.filter_by(good_id=good_id).all()
        response = [{
            'id': review.id,
            'username': review.username,
            'rating': review.rating,
            'comment': decrypt_data(review.comment),
            'status': review.status
        } for review in reviews]

        log_to_audit("reviews_service", f"/reviews/product/{good_id}", "success", f"Retrieved reviews for good_id {good_id}")
        return jsonify(response)


class GetCustomerReviews(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @circuit_breaker
    def get(self, username):
        reviews = Review.query.filter_by(username=username).all()
        response = [{
            'id': review.id,
            'good_id': review.good_id,
            'rating': review.rating,
            'comment': decrypt_data(review.comment),
            'status': review.status
        } for review in reviews]

        log_to_audit("reviews_service", f"/reviews/customer/{username}", "success", f"Retrieved reviews for {username}")
        return jsonify(response)


class ModerateReview(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def put(self, review_id):
        data = request.json
        status = data.get('status')
        if status not in ["approved", "flagged"]:
            return {"error": "Invalid status"}, 400

        review = Review.query.get(review_id)
        if not review:
            log_to_audit(
                service_name="reviews_service",
                endpoint=f"/reviews/moderate/{review_id}",
                status="error",
                details="Review not found"
            )
            return {"error": "Review not found"}, 404

        review.status = status
        db.session.commit()
        log_to_audit(
            service_name="reviews_service",
            endpoint=f"/reviews/moderate/{review_id}",
            status="success",
            details=f"Moderated review {review_id} to status {status}"
        )
        return {"message": "Review status updated successfully"}, 200


class GetReviewDetails(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @circuit_breaker
    def get(self, review_id):
        review = Review.query.get(review_id)
        if not review:
            log_to_audit(
                service_name="reviews_service",
                endpoint=f"/reviews/details/{review_id}",
                status="error",
                details="Review not found"
            )
            return {"error": "Review not found"}, 404

        response = {
            'id': review.id,
            'good_id': review.good_id,
            'username': review.username,
            'rating': review.rating,
            'comment': decrypt_data(review.comment),
            'status': review.status
        }

        log_to_audit(
            service_name="reviews_service",
            endpoint=f"/reviews/details/{review_id}",
            status="success",
            details=f"Retrieved details for review {review_id}"
        )
        return jsonify(response)


# Add API routes
api.add_resource(SubmitReview, '/reviews')
api.add_resource(UpdateReview, '/reviews/<int:review_id>')
api.add_resource(DeleteReview, '/reviews/<int:review_id>')
api.add_resource(GetProductReviews, '/reviews/product/<int:good_id>')
api.add_resource(GetCustomerReviews, '/reviews/customer/<string:username>')
api.add_resource(ModerateReview, '/reviews/moderate/<int:review_id>')
api.add_resource(GetReviewDetails, '/reviews/details/<int:review_id>')
