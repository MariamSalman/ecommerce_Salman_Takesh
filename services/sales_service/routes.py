from flask_restful import Api, Resource
from models import Good, Sale
from database import db
from flask import request, jsonify
from datetime import datetime

api = Api()

class DisplayGoods(Resource):
    def get(self):
        goods = Good.query.filter(Good.stock_count > 0).all()
        return jsonify([{
            'id': good.id,
            'name': good.name,
            'price': good.price
        } for good in goods])

class GetGoodDetails(Resource):
    def get(self, good_id):
        good = Good.query.get(good_id)
        if not good:
            return {"error": "Good not found"}, 404
        return {
            'id': good.id,
            'name': good.name,
            'category': good.category,
            'price': good.price,
            'stock_count': good.stock_count
        }

class MakeSale(Resource):
    def post(self):
        data = request.json
        username = data.get('username')
        good_id = data.get('good_id')
        quantity = data.get('quantity')

        # Validate inputs
        good = Good.query.get(good_id)
        if not good or good.stock_count < quantity:
            return {"error": "Item not available or insufficient stock"}, 400

        # Update stock count
        good.stock_count -= quantity
        db.session.add(good)

        # Record the sale
        sale = Sale(
            good_id=good_id,
            username=username,
            quantity=quantity,
            timestamp=datetime.now()
        )
        db.session.add(sale)
        db.session.commit()

        return {"message": "Sale completed successfully"}, 200

class GetPurchaseHistory(Resource):
    def get(self, username):
        sales = Sale.query.filter_by(username=username).all()
        return jsonify([{
            'good_id': sale.good_id,
            'quantity': sale.quantity,
            'timestamp': sale.timestamp.isoformat()
        } for sale in sales])

api.add_resource(DisplayGoods, '/sales/goods')
api.add_resource(GetGoodDetails, '/sales/goods/<int:good_id>')
api.add_resource(MakeSale, '/sales/purchase')
api.add_resource(GetPurchaseHistory, '/sales/history/<username>')


