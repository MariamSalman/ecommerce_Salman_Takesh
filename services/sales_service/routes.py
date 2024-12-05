from flask_restful import Api, Resource
from models import Good, Sale
from database import db
from flask import request, jsonify
from utils import log_to_audit, call_service_api

api = Api()

CUSTOMERS_SERVICE_URL = "http://127.0.0.1:5001"  # Replace with actual Customers Service URL

# Route: Display Available Goods
class DisplayGoods(Resource):
    def get(self):
        goods = Good.query.all()
        goods_list = [{
            "id": g.id,
            "name": g.name,
            "price": g.price
        } for g in goods]

        # Log action
        log_to_audit(
            service_name="sales_service",
            endpoint="/sales/goods",
            status="success",
            details="Retrieved all available goods"
        )
        return jsonify(goods_list)

# Route: Get Good Details
class GetGoodDetails(Resource):
    def get(self, good_id):
        good = Good.query.get(good_id)
        if not good:
            log_to_audit(
                service_name="sales_service",
                endpoint=f"/sales/goods/{good_id}",
                status="error",
                details="Good not found"
            )
            return {"error": "Good not found"}, 404

        # Log action
        log_to_audit(
            service_name="sales_service",
            endpoint=f"/sales/goods/{good_id}",
            status="success",
            details=f"Retrieved details for good ID {good_id}"
        )
        return jsonify({
            "id": good.id,
            "name": good.name,
            "category": good.category,
            "price": good.price,
            "stock_count": good.stock_count
        })

# Route: Make a Sale
class MakeSale(Resource):
    def post(self):
        data = request.json
        username = data.get('username')
        good_id = data.get('good_id')
        quantity = data.get('quantity', 1)

        # Validate input
        if not username or not good_id or quantity <= 0:
            return {"error": "Invalid input: username, good_id, and quantity must be valid"}, 400

        # Retrieve the good
        good = Good.query.get(good_id)
        if not good:
            return {"error": "Good not found"}, 404

        # Check stock availability
        if good.stock_count < quantity:
            return {"error": "Not enough stock available"}, 400

        # Retrieve wallet balance from Customers Service
        try:
            response = call_service_api(
                method="GET",
                url=f"{CUSTOMERS_SERVICE_URL}/customers/username/{username}"
            )
            if response.status_code != 200:
                return {"error": "Customer not found"}, 404
            customer_data = response.json()
            wallet_balance = customer_data.get("wallet_balance", 0.0)
        except Exception as e:
            return {"error": f"Error communicating with Customers Service: {e}"}, 500

        # Check wallet balance
        total_cost = good.price * quantity
        if wallet_balance < total_cost:
            return {"error": "Insufficient wallet balance"}, 400

        # Deduct wallet balance via Customers Service
        try:
            update_response = call_service_api(
                method="PUT",
                url=f"{CUSTOMERS_SERVICE_URL}/customers/{customer_data['id']}/wallet",
                payload={"amount": -total_cost}
            )
            if update_response.status_code != 200:
                return {"error": "Failed to update wallet balance"}, 500
        except Exception as e:
            return {"error": f"Error communicating with Customers Service: {e}"}, 500

        # Process sale
        good.stock_count -= quantity
        sale = Sale(good_id=good.id, username=username, quantity=quantity)
        db.session.add(sale)
        db.session.commit()

        # Log sale
        log_to_audit(
            service_name="sales_service",
            endpoint="/sales/purchase",
            status="success",
            details=f"Processed sale for good ID {good_id} by user {username}, quantity {quantity}"
        )
        return {"message": "Sale completed successfully"}, 201

# Route: Get Purchase History
class GetPurchaseHistory(Resource):
    def get(self, username):
        sales = Sale.query.filter_by(username=username).all()
        if not sales:
            log_to_audit(
                service_name="sales_service",
                endpoint=f"/sales/history/{username}",
                status="error",
                details="No purchase history found"
            )
            return {"error": "No purchase history found"}, 404

        history = [{
            "good_id": s.good_id,
            "quantity": s.quantity,
            "timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for s in sales]

        # Log action
        log_to_audit(
            service_name="sales_service",
            endpoint=f"/sales/history/{username}",
            status="success",
            details=f"Retrieved purchase history for user {username}"
        )
        return jsonify(history)

# Add resources to API
api.add_resource(DisplayGoods, '/sales/goods')
api.add_resource(GetGoodDetails, '/sales/goods/<int:good_id>')
api.add_resource(MakeSale, '/sales/purchase')
api.add_resource(GetPurchaseHistory, '/sales/history/<string:username>')
