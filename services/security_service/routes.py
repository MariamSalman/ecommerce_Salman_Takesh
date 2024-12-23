from flask_restful import Api, Resource
from models import AuditLog, SecureKey
from database import db
from flask import request, jsonify
from extensions import limiter  # Import limiter
from cryptography.fernet import Fernet
import os

api = Api()

# Generate or retrieve encryption key (In production, use a secure key management service)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

# Encryption Utilities
def encrypt_data(data):
    """
    Encrypts the given data using the Fernet cipher suite.
    
    Args:
        data (str): The data to encrypt.
    
    Returns:
        str: The encrypted data as a string.
    """
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(data):
    """
    Decrypts the given encrypted data using the Fernet cipher suite.
    
    Args:
        data (str): The encrypted data to decrypt.
    
    Returns:
        str: The decrypted data as a string.
    """
    if not data:
        return None
    return cipher_suite.decrypt(data.encode()).decode()


class AuditLogsAPI(Resource):
    """
    API Resource for handling audit logs. Provides methods to retrieve and create logs.
    """
    decorators = [limiter.limit("50/minute")]  # Limit this endpoint to 50 requests per minute

    def get(self):
        """
        Retrieves all audit logs from the database.

        Returns:
            list: A list of all audit logs in JSON format.
        """
        logs = AuditLog.query.all()
        return jsonify([{
            'id': log.id,
            'timestamp': log.timestamp,
            'service': log.service,
            'operation': log.operation,
            'status': log.status,
            'user': log.user,
            'details': log.details
        } for log in logs])

    decorators = [limiter.limit("10/minute")]  # Limit this endpoint to 10 requests per minute

    def post(self):
        """
        Creates a new audit log entry.

        Args:
            data (dict): The data to create the log entry. Expected fields: 'service', 'operation', 'status', 'user', 'details'.
        
        Returns:
            dict: Confirmation message if log was successfully added or error message if fields are missing.
        """
        data = request.json
        if not data or not all(key in data for key in ['service', 'operation', 'status']):
            return {"error": "Missing required fields"}, 400

        log = AuditLog(
            service=data.get('service'),
            operation=data.get('operation'),
            status=data.get('status'),
            user=data.get('user', None),
            details=data.get('details', None)
        )
        db.session.add(log)
        db.session.commit()
        return {"message": "Log added successfully"}, 201


class SecureKeysAPI(Resource):
    """
    API Resource for managing secure keys. Allows for storing and retrieving encrypted keys.
    """
    decorators = [limiter.limit("20/minute")]  # Limit this endpoint to 20 requests per minute

    def post(self):
        """
        Stores an encrypted key in the database.
        
        Args:
            data (dict): The data to store the key. Expected fields: 'key_name', 'key_value'.
        
        Returns:
            dict: Confirmation message if key was successfully stored or error message if fields are missing.
        """
        data = request.json
        key_name = data.get('key_name')
        key_value = data.get('key_value')
        if not key_name or not key_value:
            return {"error": "Key name and value are required"}, 400

        encrypted_value = encrypt_data(key_value)
        key = SecureKey(key_name=key_name, key_value=encrypted_value)
        db.session.add(key)
        db.session.commit()
        return {"message": "Key stored successfully"}, 201

    decorators = [limiter.limit("20/minute")]  # Limit this endpoint to 20 requests per minute

    def get(self, key_name):
        """
        Retrieves the encrypted key from the database and decrypts it.

        Args:
            key_name (str): The name of the key to retrieve.

        Returns:
            dict: The decrypted key value if found, or an error message if the key is not found.
        """
        key = SecureKey.query.filter_by(key_name=key_name).first()
        if not key:
            return {"error": "Key not found"}, 404

        decrypted_value = decrypt_data(key.key_value)
        return {"key_value": decrypted_value}


# Add resources to API
api.add_resource(AuditLogsAPI, '/audit_logs')
api.add_resource(SecureKeysAPI, '/secure_keys', '/secure_keys/<string:key_name>')

