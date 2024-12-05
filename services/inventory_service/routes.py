from flask_restful import Api, Resource
from models import Good
from database import db
from flask import request, jsonify

api = Api()

class AddGood(Resource):
    def post(self):
        data = request.json
        name = data.get('name')
        category = data.get('category')
        price = data.get('price')
        description = data.get('description')
        stock_count = data.get('stock_count')

        if not all([name, category, price, stock_count]):
            return {"error": "Name, category, price, and stock_count are required"}, 400

        good = Good(name=name, category=category, price=price, description=description, stock_count=stock_count)
        db.session.add(good)
        db.session.commit()
        return {"message": "Good added successfully"}, 201

class DeductGood(Resource):
    def put(self, good_id):
        data = request.json
        quantity = data.get('quantity')

        if quantity is None or quantity <= 0:
            return {"error": "Quantity must be greater than zero"}, 400

        good = Good.query.get(good_id)
        if not good:
            return {"error": "Good not found"}, 404

        if good.stock_count < quantity:
            return {"error": "Not enough stock available"}, 400

        good.stock_count -= quantity
        db.session.commit()
        return {"message": "Stock updated successfully", "new_stock": good.stock_count}, 200

class UpdateGood(Resource):
    def put(self, good_id):
        data = request.json
        good = Good.query.get(good_id)

        if not good:
            return {"error": "Good not found"}, 404

        good.name = data.get('name', good.name)
        good.category = data.get('category', good.category)
        good.price = data.get('price', good.price)
        good.description = data.get('description', good.description)
        good.stock_count = data.get('stock_count', good.stock_count)

        db.session.commit()
        return {"message": "Good updated successfully"}, 200

class GetAllGoods(Resource):
    def get(self):
        goods = Good.query.all()
        return jsonify([{
            "id": g.id,
            "name": g.name,
            "category": g.category,
            "price": g.price,
            "description": g.description,
            "stock_count": g.stock_count
        } for g in goods])

api.add_resource(AddGood, '/goods')
api.add_resource(DeductGood, '/goods/<int:good_id>/deduct')
api.add_resource(UpdateGood, '/goods/<int:good_id>')
api.add_resource(GetAllGoods, '/goods')
