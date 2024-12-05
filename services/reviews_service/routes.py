from flask_restful import Api, Resource
from models import Review
from database import db
from flask import request, jsonify
from utils import log_to_audit, encrypt_data, decrypt_data, breaker
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address  # Import the correct key function

api = Api()

# Initialize Limiter with a key function
limiter = Limiter(key_func=get_remote_address)

class SubmitReview(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @breaker
    def post(self):
        """
        Submits a new review for a product.

        Request Body:
        {
            "good_id": "int",
            "username": "string",
            "rating": "int",
            "comment": "string"
        }

        Response:
        - 201 Created: Review successfully submitted.
          {
            "message": "Review submitted successfully"
          }
        - 400 Bad Request: Missing required fields or invalid rating value.
          {
            "error": "All fields (good_id, username, rating, comment) are required"
          }

        This endpoint allows users to submit a review for a product. It validates the data, encrypts the comment, 
        and stores the review in the database. If successful, it returns a success message.
        """
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

    @breaker
    def put(self, review_id):
        """
        Updates an existing review.

        Request Body:
        {
            "rating": "int",
            "comment": "string"
        }

        Response:
        - 200 OK: Review successfully updated.
          {
            "message": "Review updated successfully"
          }
        - 404 Not Found: Review not found by `review_id`.
          {
            "error": "Review not found"
          }

        This endpoint allows users to update the rating and/or comment of an existing review. 
        The comment is encrypted before storing in the database.
        """
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

    @breaker
    def delete(self, review_id):
        """
        Deletes a review by `review_id`.

        Response:
        - 200 OK: Review successfully deleted.
          {
            "message": "Review deleted successfully"
          }
        - 404 Not Found: Review not found by `review_id`.
          {
            "error": "Review not found"
          }

        This endpoint deletes a specific review from the database.
        """
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

    @breaker
    def get(self, good_id):
        """
        Retrieves all reviews for a specific product.

        Response:
        - 200 OK: List of reviews for the product.
          [
            {
              "id": "int",
              "username": "string",
              "rating": "int",
              "comment": "string",
              "status": "string"
            }
          ]
        - 404 Not Found: No reviews found for the product.
          {
            "message": "No reviews found for the product"
          }

        This endpoint retrieves reviews for a specific product identified by `good_id`. The comment is decrypted before returning.
        """
        try:
            reviews = Review.query.filter_by(good_id=good_id).all()
            if not reviews:
                return {"message": "No reviews found for the product"}, 404

            response = [{
                'id': review.id,
                'username': review.username,
                'rating': review.rating,
                'comment': decrypt_data(review.comment),
                'status': review.status
            } for review in reviews]

            log_to_audit("reviews_service", f"/reviews/product/{good_id}", "success", f"Retrieved reviews for good_id {good_id}")
            return jsonify(response)
        except Exception as e:
            log_to_audit("reviews_service", f"/reviews/product/{good_id}", "error", f"Error occurred: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}, 500

class GetCustomerReviews(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @breaker
    def get(self, username):
        """
        Retrieves all reviews for a specific customer.

        Response:
        - 200 OK: List of reviews for the customer.
          [
            {
              "id": "int",
              "good_id": "int",
              "rating": "int",
              "comment": "string",
              "status": "string"
            }
          ]

        This endpoint retrieves all reviews submitted by a specific customer, identified by `username`.
        """
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

    @breaker
    def put(self, review_id):
        """
        Moderates a review by updating its status.

        Request Body:
        {
            "status": "string"  # "approved" or "flagged"
        }

        Response:
        - 200 OK: Review status updated successfully.
          {
            "message": "Review status updated successfully"
          }
        - 404 Not Found: Review not found by `review_id`.
          {
            "error": "Review not found"
          }
        - 400 Bad Request: Invalid status value.
          {
            "error": "Invalid status"
          }

        This endpoint updates the status of a review to either "approved" or "flagged".
        """
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

    @breaker
    def get(self, review_id):
        """
        Retrieves the details of a specific review.

        Response:
        - 200 OK: Review details.
          {
            "id": "int",
            "good_id": "int",
            "username": "string",
            "rating": "int",
            "comment": "string",
            "status": "string"
          }
        - 404 Not Found: Review not found by `review_id`.
          {
            "error": "Review not found"
          }

        This endpoint retrieves detailed information for a specific review.
        """
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
