from flask_restful import Api, Resource
from models import Good
from database import db
from flask import request, jsonify
from utils import log_to_audit, encrypt_data, decrypt_data, circuit_breaker
from extensions import limiter

api = Api()

class AddGood(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    @circuit_breaker
    def post(self):
        """
        Adds a new product to the inventory.

        Request Body:
        {
            "name": "string",
            "category": "string",
            "price": "float",
            "description": "string",
            "stock_count": "int"
        }

        Response:
        - 201 Created: Good successfully added.
          {
            "message": "Good added successfully"
          }
        - 400 Bad Request: Missing required fields (name, category, price, stock_count).
          {
            "error": "Name, category, price, and stock_count are required"
          }

        This endpoint checks for the required fields, encrypts the description (if provided), 
        and adds the good to the database. All actions are logged for auditing purposes.
        """
        data = request.json
        name = data.get('name')
        category = data.get('category')
        price = data.get('price')
        description = data.get('description')
        stock_count = data.get('stock_count')

        if not all([name, category, price, stock_count]):
            log_to_audit("inventory_service", "/goods", "error", details="Missing required fields")
            return {"error": "Name, category, price, and stock_count are required"}, 400

        encrypted_description = encrypt_data(description) if description else None
        good = Good(name=name, category=category, price=price, description=encrypted_description, stock_count=stock_count)
        db.session.add(good)
        db.session.commit()

        log_to_audit("inventory_service", "/goods", "success", details=f"Added good: {name}")
        return {"message": "Good added successfully"}, 201

class DeductGood(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def put(self, good_id):
        """
        Deducts a specified quantity from the stock of a good.

        Request Body:
        {
            "quantity": "int"
        }

        Response:
        - 200 OK: Stock successfully updated.
          {
            "message": "Stock updated successfully",
            "new_stock": "int"
          }
        - 400 Bad Request: Invalid quantity (must be greater than zero).
          {
            "error": "Quantity must be greater than zero"
          }
        - 404 Not Found: Good not found by `good_id`.
          {
            "error": "Good not found"
          }
        - 400 Bad Request: Insufficient stock.
          {
            "error": "Not enough stock available"
          }

        This endpoint updates the stock of a specified good by deducting the given quantity.
        If the stock is insufficient or invalid, an error is returned. All actions are logged for auditing.
        """
        data = request.json
        quantity = data.get('quantity')

        if quantity is None or quantity <= 0:
            log_to_audit("inventory_service", f"/goods/{good_id}/deduct", "error", details="Invalid quantity")
            return {"error": "Quantity must be greater than zero"}, 400

        good = Good.query.get(good_id)
        if not good:
            log_to_audit("inventory_service", f"/goods/{good_id}/deduct", "error", details="Good not found")
            return {"error": "Good not found"}, 404

        if good.stock_count < quantity:
            log_to_audit("inventory_service", f"/goods/{good_id}/deduct", "error", details="Insufficient stock")
            return {"error": "Not enough stock available"}, 400

        good.stock_count -= quantity
        db.session.commit()

        log_to_audit("inventory_service", f"/goods/{good_id}/deduct", "success", details=f"Deducted {quantity} units")
        return {"message": "Stock updated successfully", "new_stock": good.stock_count}, 200

class UpdateGood(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit this endpoint to 5 requests per minute

    @circuit_breaker
    def put(self, good_id):
        """
        Updates the details of an existing good.

        Request Body:
        {
            "name": "string",
            "category": "string",
            "price": "float",
            "description": "string",
            "stock_count": "int"
        }

        Response:
        - 200 OK: Good successfully updated.
          {
            "message": "Good updated successfully"
          }
        - 404 Not Found: Good not found by `good_id`.
          {
            "error": "Good not found"
          }

        This endpoint allows updating the details of a product. The description is encrypted before storing in the database.
        All actions are logged for auditing purposes.
        """
        data = request.json
        good = Good.query.get(good_id)

        if not good:
            log_to_audit("inventory_service", f"/goods/{good_id}", "error", details="Good not found")
            return {"error": "Good not found"}, 404

        good.name = data.get('name', good.name)
        good.category = data.get('category', good.category)
        good.price = data.get('price', good.price)
        good.description = encrypt_data(data.get('description')) if data.get('description') else good.description
        good.stock_count = data.get('stock_count', good.stock_count)

        db.session.commit()

        log_to_audit("inventory_service", f"/goods/{good_id}", "success", details=f"Updated good ID {good_id}")
        return {"message": "Good updated successfully"}, 200

class GetAllGoods(Resource):
    decorators = [limiter.limit("20/minute")]  # Limit this endpoint to 20 requests per minute

    @circuit_breaker
    def get(self):
        """
        Retrieves all goods from the inventory.

        Response:
        - 200 OK: Returns a list of all goods in the inventory.
          [
            {
              "id": "int",
              "name": "string",
              "category": "string",
              "price": "float",
              "description": "string",
              "stock_count": "int"
            }
          ]

        This endpoint retrieves all products in the inventory, decrypting their description before returning.
        All actions are logged for auditing purposes.
        """
        goods = Good.query.all()
        goods_list = [
            {
                "id": g.id,
                "name": g.name,
                "category": g.category,
                "price": g.price,
                "description": decrypt_data(g.description) if g.description else None,
                "stock_count": g.stock_count
            }
            for g in goods
        ]

        log_to_audit("inventory_service", "/goods", "success", details="Retrieved all goods")
        return jsonify(goods_list)


# Add API resources
api.add_resource(AddGood, '/goods')
api.add_resource(DeductGood, '/goods/<int:good_id>/deduct')
api.add_resource(UpdateGood, '/goods/<int:good_id>')
api.add_resource(GetAllGoods, '/goods')
