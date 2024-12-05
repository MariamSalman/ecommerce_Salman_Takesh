from flask_restful import Api, Resource
from models import Good, Sale
from database import db
from flask import request, jsonify
from utils import log_to_audit, call_service_api, circuit_breaker
from extensions import limiter  # Ensure limiter is imported from extensions.py

api = Api()

CUSTOMERS_SERVICE_URL = "http://127.0.0.1:5001"  # Replace with the actual Customers Service URL


class DisplayGoods(Resource):
    decorators = [limiter.limit("20/minute")]  # Limit this endpoint to 20 requests per minute

    @circuit_breaker
    def get(self):
        try:
            goods = Good.query.all()
            goods_list = [{
                "id": g.id,
                "name": g.name,
                "price": g.price
            } for g in goods]

            log_to_audit("sales_service", "/sales/goods", "success", "Retrieved all goods")
            return jsonify(goods_list)
        except Exception as e:
            log_to_audit("sales_service", "/sales/goods", "error", f"Failed to retrieve goods: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500


class GetGoodDetails(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @circuit_breaker
    def get(self, good_id):
        try:
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
        except Exception as e:
            log_to_audit("sales_service", f"/sales/goods/{good_id}", "error", f"Failed to fetch good details: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500


class MakeSale(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def post(self):
        data = request.json
        username = data.get('username')
        good_id = data.get('good_id')
        quantity = data.get('quantity', 1)

        if not username or not good_id or quantity <= 0:
            return {"error": "Invalid input: username, good_id, and quantity must be valid"}, 400

        try:
            good = Good.query.get(good_id)
            if not good:
                return {"error": "Good not found"}, 404

            if good.stock_count < quantity:
                return {"error": "Not enough stock available"}, 400

            # Call Customers Service to fetch customer data
            response = call_service_api("GET", f"{CUSTOMERS_SERVICE_URL}/customers/username/{username}")
            if response.status_code != 200:
                return {"error": "Customer not found"}, 404
            customer_data = response.json()
            wallet_balance = customer_data.get("wallet_balance", 0.0)

            total_cost = good.price * quantity
            if wallet_balance < total_cost:
                return {"error": "Insufficient wallet balance"}, 400

            # Deduct wallet balance
            update_response = call_service_api(
                "PUT", f"{CUSTOMERS_SERVICE_URL}/customers/{customer_data['id']}/wallet", {"amount": -total_cost}
            )
            if update_response.status_code != 200:
                return {"error": "Failed to update wallet balance"}, 500

            # Deduct stock and log sale
            good.stock_count -= quantity
            sale = Sale(good_id=good.id, username=username, quantity=quantity)
            db.session.add(sale)
            db.session.commit()

            log_to_audit("sales_service", "/sales/purchase", "success", f"Processed sale for {username}, good ID {good_id}")
            return {"message": "Sale completed successfully"}, 201
        except Exception as e:
            log_to_audit("sales_service", "/sales/purchase", "error", f"Sale failed: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500


class GetPurchaseHistory(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def get(self, username):
        try:
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
        except Exception as e:
            log_to_audit("sales_service", f"/sales/history/{username}", "error", f"Failed to fetch purchase history: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500


# Add resources to API
api.add_resource(DisplayGoods, '/sales/goods')
api.add_resource(GetGoodDetails, '/sales/goods/<int:good_id>')
api.add_resource(MakeSale, '/sales/purchase')
api.add_resource(GetPurchaseHistory, '/sales/history/<string:username>')
