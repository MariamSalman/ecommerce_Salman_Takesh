from flask_restful import Api, Resource
from models import Good, Sale
from database import db
from flask import request, jsonify

api = Api()

class DisplayGoods(Resource):
    def get(self):
        goods = Good.query.all()
        return jsonify([{
            "name": g.name,
            "price": g.price
        } for g in goods])

class GetGoodDetails(Resource):
    def get(self, good_id):
        good = Good.query.get(good_id)
        if not good:
            return {"error": "Good not found"}, 404
        return jsonify({
            "name": good.name,
            "category": good.category,
            "price": good.price,
            "stock_count": good.stock_count
        })

CUSTOMERS_SERVICE_URL = "http://127.0.0.1:5001"  # Replace with actual Customers Service URL

import requests

CUSTOMERS_SERVICE_URL = "http://127.0.0.1:5001"  # Replace with actual Customers Service URL

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
            response = requests.get(f"{CUSTOMERS_SERVICE_URL}/customers/username/{username}")
            if response.status_code != 200:
                return {"error": "Customer not found"}, 404  # Proper error handling
            customer_data = response.json()
            wallet_balance = customer_data.get("wallet_balance", 0.0)
        except requests.exceptions.RequestException:
            return {"error": "Unable to connect to Customers Service"}, 500

        # Check wallet balance
        total_cost = good.price * quantity
        if wallet_balance < total_cost:
            return {"error": "Insufficient wallet balance"}, 400

        # Deduct wallet balance via Customers Service
        try:
            update_response = requests.put(
                f"{CUSTOMERS_SERVICE_URL}/customers/{customer_data['id']}/wallet",
                json={"amount": -total_cost}
            )
            if update_response.status_code != 200:
                return {"error": "Failed to update wallet balance"}, 500
        except requests.exceptions.RequestException:
            return {"error": "Unable to connect to Customers Service"}, 500

        # Process sale
        good.stock_count -= quantity
        sale = Sale(good_id=good.id, username=username, quantity=quantity)
        db.session.add(sale)
        db.session.commit()

        return {"message": "Sale completed successfully"}, 201



class GetPurchaseHistory(Resource):
    def get(self, username):
        sales = Sale.query.filter_by(username=username).all()
        return jsonify([{
            "good_id": s.good_id,
            "quantity": s.quantity,
            "timestamp": s.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        } for s in sales])

api.add_resource(DisplayGoods, '/sales/goods')
api.add_resource(GetGoodDetails, '/sales/goods/<int:good_id>')
api.add_resource(MakeSale, '/sales/purchase')
api.add_resource(GetPurchaseHistory, '/sales/history/<string:username>')
