from flask_restful import Api, Resource
from models import Good, Sale
from database import db
from flask import request, jsonify
from utils import log_to_audit, call_service_api, circuit_breaker
from flask_limiter import Limiter

api = Api()

CUSTOMERS_SERVICE_URL = "http://127.0.0.1:5001"  # Replace with the actual Customers Service URL

# DisplayGoods Resource
class DisplayGoods(Resource):
    decorators = [limiter.limit("20/minute")]  # Limit this endpoint to 20 requests per minute

    @circuit_breaker
    def get(self):
        """
        Retrieves all goods available for sale.

        Response:
        - 200 OK: A list of goods with their id, name, and price.
          [
              {
                  "id": "int",
                  "name": "string",
                  "price": "float"
              }
          ]
        """
        goods = Good.query.all()
        goods_list = [{
            "id": g.id,
            "name": g.name,
            "price": g.price
        } for g in goods]

        log_to_audit("sales_service", "/sales/goods", "success", "Retrieved all goods")
        return jsonify(goods_list)

# GetGoodDetails Resource
class GetGoodDetails(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @circuit_breaker
    def get(self, good_id):
        """
        Retrieves details of a specific good.

        Args:
        - good_id (int): The ID of the good to fetch details for.

        Response:
        - 200 OK: Details of the good.
          {
              "id": "int",
              "name": "string",
              "category": "string",
              "price": "float",
              "stock_count": "int"
          }
        - 404 Not Found: If the good with the given ID doesn't exist.
          {
              "error": "Good not found"
          }
        """
        good = Good.query.get(good_id)
        if not good:
            log_to_audit("sales_service", f"/sales/goods/{good_id}", "error", "Good not found")
            return {"error": "Good not found"}, 404

        log_to_audit("sales_service", f"/sales/goods/{good_id}", "success", f"Details for good ID {good_id}")
        return jsonify({
            "id": good.id,
            "name": good.name,
            "category": good.category,
            "price": good.price,
            "stock_count": good.stock_count
        })

# MakeSale Resource
class MakeSale(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def post(self):
        """
        Processes a sale by deducting stock and updating customer wallet.

        Args:
        - username (str): The username of the customer.
        - good_id (int): The ID of the good being purchased.
        - quantity (int): The quantity of the good to purchase (defaults to 1).

        Response:
        - 201 Created: If the sale is processed successfully.
          {
              "message": "Sale completed successfully"
          }
        - 400 Bad Request: If any input is invalid (e.g., insufficient stock, invalid quantity).
          {
              "error": "Invalid input"
          }
        - 404 Not Found: If the good or customer is not found.
          {
              "error": "Good not found" / "Customer not found"
          }
        - 500 Internal Server Error: If there is an issue with the communication to the Customers Service.
          {
              "error": "Error message"
          }
        """
        data = request.json
        username = data.get('username')
        good_id = data.get('good_id')
        quantity = data.get('quantity', 1)

        if not username or not good_id or quantity <= 0:
            return {"error": "Invalid input: username, good_id, and quantity must be valid"}, 400

        good = Good.query.get(good_id)
        if not good:
            return {"error": "Good not found"}, 404

        if good.stock_count < quantity:
            return {"error": "Not enough stock available"}, 400

        try:
            response = call_service_api("GET", f"{CUSTOMERS_SERVICE_URL}/customers/username/{username}")
            if response.status_code != 200:
                return {"error": "Customer not found"}, 404
            customer_data = response.json()
            wallet_balance = customer_data.get("wallet_balance", 0.0)
        except Exception as e:
            return {"error": f"Error communicating with Customers Service: {e}"}, 500

        total_cost = good.price * quantity
        if wallet_balance < total_cost:
            return {"error": "Insufficient wallet balance"}, 400

        try:
            update_response = call_service_api(
                "PUT", f"{CUSTOMERS_SERVICE_URL}/customers/{customer_data['id']}/wallet", {"amount": -total_cost}
            )
            if update_response.status_code != 200:
                return {"error": "Failed to update wallet balance"}, 500
        except Exception as e:
            return {"error": f"Error communicating with Customers Service: {e}"}, 500

        good.stock_count -= quantity
        sale = Sale(good_id=good.id, username=username, quantity=quantity)
        db.session.add(sale)
        db.session.commit()

        log_to_audit("sales_service", "/sales/purchase", "success", f"Processed sale for {username}, good ID {good_id}")
        return {"message": "Sale completed successfully"}, 201

# GetPurchaseHistory Resource
class GetPurchaseHistory(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def get(self, username):
        """
        Retrieves the purchase history for a customer.

        Args:
        - username (str): The username of the customer.

        Response:
        - 200 OK: A list of the customer's purchase history.
          [
              {
                  "good_id": "int",
                  "quantity": "int",
                  "timestamp": "string"
              }
          ]
        - 404 Not Found: If no purchase history is found for the given username.
          {
              "error": "No purchase history found"
          }
        """
        sales = Sale.query.filter_by(username=username).all()
        if not sales:
            log_to_audit("sales_service", f"/sales/history/{username}", "error", "No purchase history found")
            return {"error": "No purchase history found"}, 404

        history = [{
            "good_id": s.good_id,
            "quantity": s.quantity,
            "timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for s in sales]

        log_to_audit("sales_service", f"/sales/history/{username}", "success", f"History for user {username}")
        return jsonify(history)


# Add resources to API
api.add_resource(DisplayGoods, '/sales/goods')
api.add_resource(GetGoodDetails, '/sales/goods/<int:good_id>')
api.add_resource(MakeSale, '/sales/purchase')
api.add_resource(GetPurchaseHistory, '/sales/history/<string:username>')
