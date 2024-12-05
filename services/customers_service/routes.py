from flask_restful import Api, Resource
from models import Customer
from database import db
from flask import request, jsonify

api = Api()

class RegisterCustomer(Resource):
    def post(self):
        data = request.json
        full_name = data.get('full_name')
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        age = data.get('age')
        address = data.get('address')
        gender = data.get('gender')
        marital_status = data.get('marital_status')

        if not full_name or not username or not password or not email:
            return {"error": "Full name, username, password, and email are required"}, 400

        if Customer.query.filter((Customer.username == username) | (Customer.email == email)).first():
            return {"error": "Customer with this username or email already exists"}, 400

        # Hash the password (use a library like bcrypt or werkzeug.security)
        from werkzeug.security import generate_password_hash
        hashed_password = generate_password_hash(password)

        customer = Customer(
            full_name=full_name,
            username=username,
            password=hashed_password,
            email=email,
            age=age,
            address=address,
            gender=gender,
            marital_status=marital_status
        )
        db.session.add(customer)
        db.session.commit()
        return {"message": "Customer registered successfully"}, 201


class UpdateCustomer(Resource):
    def put(self, customer_id):
        data = request.json
        customer = Customer.query.get(customer_id)

        if not customer:
            return {"error": "Customer not found"}, 404

        customer.username = data.get('username', customer.username)
        customer.email = data.get('email', customer.email)
        db.session.commit()
        return {"message": "Customer updated successfully"}, 200

class DeleteCustomer(Resource):
    def delete(self, customer_id):
        customer = Customer.query.get(customer_id)

        if not customer:
            return {"error": "Customer not found"}, 404

        db.session.delete(customer)
        db.session.commit()
        return {"message": "Customer deleted successfully"}, 200

class GetCustomers(Resource):
    def get(self):
        customers = Customer.query.all()
        return jsonify([{
            "id": c.id,
            "full_name": c.full_name,
            "username": c.username,
            "email": c.email,
            "age": c.age,
            "address": c.address,
            "gender": c.gender,
            "marital_status": c.marital_status,
            "wallet_balance": c.wallet_balance,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        } for c in customers])


class WalletOperation(Resource):
    def put(self, customer_id):
        data = request.json
        amount = data.get('amount')

        if amount is None:
            return {"error": "Amount is required"}, 400

        customer = Customer.query.get(customer_id)
        if not customer:
            return {"error": "Customer not found"}, 404

        customer.wallet_balance += amount
        db.session.commit()

        return {
            "message": "Wallet balance updated",
            "new_balance": customer.wallet_balance
        }, 200


class GetCustomerByUsername(Resource):
    def get(self, username):
        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            return {"error": "Customer not found"}, 404
        return jsonify({
            "id": customer.id,
            "full_name": customer.full_name,
            "username": customer.username,
            "email": customer.email,
            "age": customer.age,
            "address": customer.address,
            "gender": customer.gender,
            "marital_status": customer.marital_status,
            "wallet_balance": customer.wallet_balance,
            "created_at": customer.created_at
        })


api.add_resource(RegisterCustomer, '/customers/register')
api.add_resource(UpdateCustomer, '/customers/<int:customer_id>')
api.add_resource(DeleteCustomer, '/customers/<int:customer_id>')
api.add_resource(GetCustomers, '/customers', '/customers/<int:customer_id>')
api.add_resource(WalletOperation, '/customers/<int:customer_id>/wallet')
api.add_resource(GetCustomerByUsername, '/customers/username/<string:username>')


