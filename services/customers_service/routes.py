from flask_restful import Api, Resource
from models import Customer
from database import db
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from utils import log_to_audit, encrypt_data, decrypt_data, circuit_breaker
from flask_limiter import Limiter

api = Api()


class RegisterCustomer(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit endpoint to 10 requests per minute

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
            log_to_audit("customers_service", "POST /customers/register", "error", details="Missing required fields")
            return {"error": "Full name, username, password, and email are required"}, 400

        if Customer.query.filter((Customer.username == username) | (Customer.email == email)).first():
            log_to_audit("customers_service", "POST /customers/register", "error", details="Duplicate username or email")
            return {"error": "Customer with this username or email already exists"}, 400

        hashed_password = generate_password_hash(password)
        encrypted_email = encrypt_data(email)
        encrypted_address = encrypt_data(address) if address else None

        customer = Customer(
            full_name=full_name,
            username=username,
            password=hashed_password,
            email=encrypted_email,
            age=age,
            address=encrypted_address,
            gender=gender,
            marital_status=marital_status
        )
        db.session.add(customer)
        db.session.commit()

        log_to_audit("customers_service", "POST /customers/register", "success", user=username, details="Customer registered")
        return {"message": "Customer registered successfully"}, 201



class UpdateCustomer(Resource):
    def put(self, customer_id):
        data = request.json
        customer = Customer.query.get(customer_id)

        if not customer:
            log_to_audit("customers_service", "PUT /customers/<int:customer_id>", "error", details="Customer not found")
            return {"error": "Customer not found"}, 404

        if "username" in data:
            customer.username = data.get('username', customer.username)
        if "email" in data:
            customer.email = encrypt_data(data.get('email', decrypt_data(customer.email)))

        db.session.commit()
        log_to_audit("customers_service", "PUT /customers/<int:customer_id>", "success", user=customer.username, details="Customer updated")
        return {"message": "Customer updated successfully"}, 200


class DeleteCustomer(Resource):
    def delete(self, customer_id):
        customer = Customer.query.get(customer_id)

        if not customer:
            log_to_audit("customers_service", "DELETE /customers/<int:customer_id>", "error", details="Customer not found")
            return {"error": "Customer not found"}, 404

        log_to_audit("customers_service", "DELETE /customers/<int:customer_id>", "success", user=customer.username, details="Customer deleted")
        db.session.delete(customer)
        db.session.commit()
        return {"message": "Customer deleted successfully"}, 200



class GetCustomers(Resource):
    def get(self):
        customers = Customer.query.all()
        log_to_audit("customers_service", "GET /customers", "success", details="Fetched all customers")
        return jsonify([{
            "id": c.id,
            "full_name": c.full_name,
            "username": c.username,
            "email": decrypt_data(c.email),
            "age": c.age,
            "address": decrypt_data(c.address) if c.address else None,
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
            log_to_audit("customers_service", "PUT /customers/<int:customer_id>/wallet", "error", details="Amount is missing")
            return {"error": "Amount is required"}, 400

        customer = Customer.query.get(customer_id)
        if not customer:
            log_to_audit("customers_service", "PUT /customers/<int:customer_id>/wallet", "error", details="Customer not found")
            return {"error": "Customer not found"}, 404

        customer.wallet_balance += amount
        db.session.commit()

        log_to_audit("customers_service", "PUT /customers/<int:customer_id>/wallet", "success", user=customer.username, details=f"Wallet updated by {amount}")
        return {
            "message": "Wallet balance updated",
            "new_balance": customer.wallet_balance
        }, 200



class GetCustomerByUsername(Resource):
    decorators = [limiter.limit("5/minute")]  # Limit endpoint to 5 requests per minute

    @circuit_breaker
    def get(self, username):
        customer = Customer.query.filter_by(username=username).first()
        if not customer:
            log_to_audit("customers_service", "GET /customers/username/<string:username>", "error", details="Customer not found")
            return {"error": "Customer not found"}, 404

        log_to_audit("customers_service", "GET /customers/username/<string:username>", "success", user=username, details="Fetched customer details")
        return jsonify({
            "id": customer.id,
            "full_name": customer.full_name,
            "username": customer.username,
            "email": decrypt_data(customer.email),
            "age": customer.age,
            "address": decrypt_data(customer.address) if customer.address else None,
            "gender": customer.gender,
            "marital_status": customer.marital_status,
            "wallet_balance": customer.wallet_balance,
            "created_at": customer.created_at
        })


api.add_resource(RegisterCustomer, '/customers/register')
api.add_resource(UpdateCustomer, '/customers/<int:customer_id>')
api.add_resource(DeleteCustomer, '/customers/<int:customer_id>')
api.add_resource(GetCustomers, '/customers')
api.add_resource(WalletOperation, '/customers/<int:customer_id>/wallet')
api.add_resource(GetCustomerByUsername, '/customers/username/<string:username>')