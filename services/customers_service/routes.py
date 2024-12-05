from flask_restful import Api, Resource
from models import Customer
from database import db
from flask import request, jsonify
from werkzeug.security import generate_password_hash
from utils import log_to_audit, encrypt_data, decrypt_data, circuit_breaker
from extensions import limiter

api = Api()

class RegisterCustomer(Resource):
    decorators = [limiter.limit("10/minute")]  # Limit endpoint to 10 requests per minute

    def post(self):
        """
        Registers a new customer in the system.

        Validates the required fields, checks for duplicate username or email,
        hashes the password, encrypts sensitive information, and adds the customer to the database.

        Returns:
            dict: Success or error message.
        """
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
    decorators = [limiter.limit("5/minute")]

    def put(self, customer_id):
        """
        Updates an existing customer's details.

        Updates username and/or email for the given customer ID.

        Returns:
            dict: Success or error message.
        """
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
    decorators = [limiter.limit("5/minute")]

    def delete(self, customer_id):
        """
        Deletes a customer from the system.

        Deletes the customer with the given customer ID from the database.

        Returns:
            dict: Success or error message.
        """
        customer = Customer.query.get(customer_id)

        if not customer:
            log_to_audit("customers_service", "DELETE /customers/<int:customer_id>", "error", details="Customer not found")
            return {"error": "Customer not found"}, 404

        log_to_audit("customers_service", "DELETE /customers/<int:customer_id>", "success", user=customer.username, details="Customer deleted")
        db.session.delete(customer)
        db.session.commit()
        return {"message": "Customer deleted successfully"}, 200

class GetCustomers(Resource):
    decorators = [limiter.limit("20/minute")]

    def get(self):
        """
        Fetches all customers from the database.

        Returns:
            dict: A list of customer records.
        """
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
    decorators = [limiter.limit("10/minute")]

    def put(self, customer_id):
        """
        Updates the wallet balance for a specific customer.

        Increases the wallet balance by the specified amount.

        Returns:
            dict: Success or error message.
        """
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

        log_to_audit("customers_service", "PUT /customers/<int:customer_id>/wallet", "success", user=customer.username, details="Wallet updated")
        return {"message": "Wallet balance updated successfully"}, 200
