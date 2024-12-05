from flask_restful import Api, Resource
from models import Good
from database import db
from flask import request, jsonify
from utils import log_to_audit, encrypt_data, decrypt_data  # Import utilities

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
            log_to_audit(
                service_name="inventory_service",
                endpoint="/goods",
                status="error",
                details="Missing required fields for adding a good"
            )
            return {"error": "Name, category, price, and stock_count are required"}, 400

        # Optionally encrypt sensitive fields like description
        encrypted_description = encrypt_data(description) if description else None

        good = Good(name=name, category=category, price=price, description=encrypted_description, stock_count=stock_count)
        db.session.add(good)
        db.session.commit()

        log_to_audit(
            service_name="inventory_service",
            endpoint="/goods",
            status="success",
            details=f"Added good: {name}"
        )
        return {"message": "Good added successfully"}, 201

class DeductGood(Resource):
    def put(self, good_id):
        data = request.json
        quantity = data.get('quantity')

        if quantity is None or quantity <= 0:
            log_to_audit(
                service_name="inventory_service",
                endpoint=f"/goods/{good_id}/deduct",
                status="error",
                details="Invalid quantity for deduction"
            )
            return {"error": "Quantity must be greater than zero"}, 400

        good = Good.query.get(good_id)
        if not good:
            log_to_audit(
                service_name="inventory_service",
                endpoint=f"/goods/{good_id}/deduct",
                status="error",
                details="Good not found"
            )
            return {"error": "Good not found"}, 404

        if good.stock_count < quantity:
            log_to_audit(
                service_name="inventory_service",
                endpoint=f"/goods/{good_id}/deduct",
                status="error",
                details="Insufficient stock for deduction"
            )
            return {"error": "Not enough stock available"}, 400

        good.stock_count -= quantity
        db.session.commit()

        log_to_audit(
            service_name="inventory_service",
            endpoint=f"/goods/{good_id}/deduct",
            status="success",
            details=f"Deducted {quantity} units from good ID {good_id}"
        )
        return {"message": "Stock updated successfully", "new_stock": good.stock_count}, 200

class UpdateGood(Resource):
    def put(self, good_id):
        data = request.json
        good = Good.query.get(good_id)

        if not good:
            log_to_audit(
                service_name="inventory_service",
                endpoint=f"/goods/{good_id}",
                status="error",
                details="Good not found"
            )
            return {"error": "Good not found"}, 404

        good.name = data.get('name', good.name)
        good.category = data.get('category', good.category)
        good.price = data.get('price', good.price)
        good.description = encrypt_data(data.get('description')) if data.get('description') else good.description
        good.stock_count = data.get('stock_count', good.stock_count)

        db.session.commit()

        log_to_audit(
            service_name="inventory_service",
            endpoint=f"/goods/{good_id}",
            status="success",
            details=f"Updated good ID {good_id}"
        )
        return {"message": "Good updated successfully"}, 200

class GetAllGoods(Resource):
    def get(self):
        goods = Good.query.all()
        goods_list = []
        for g in goods:
            goods_list.append({
                "id": g.id,
                "name": g.name,
                "category": g.category,
                "price": g.price,
                "description": decrypt_data(g.description) if g.description else None,
                "stock_count": g.stock_count
            })

        log_to_audit(
            service_name="inventory_service",
            endpoint="/goods",
            status="success",
            details="Retrieved all goods"
        )
        return jsonify(goods_list)

api.add_resource(AddGood, '/goods')
api.add_resource(DeductGood, '/goods/<int:good_id>/deduct')
api.add_resource(UpdateGood, '/goods/<int:good_id>')
api.add_resource(GetAllGoods, '/goods')
