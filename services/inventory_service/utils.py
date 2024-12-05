import requests
from cryptography.fernet import Fernet
import os
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Encryption key
# Use a secure key management system in production.
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# Logging Function
def log_to_audit(service_name, endpoint, status, user=None, details=""):
    """
    Logs audit information to the Security Service.

    :param service_name: Name of the service
    :param endpoint: API endpoint
    :param status: Status of the operation ("success" or "error")
    :param user: Username associated with the operation (optional)
    :param details: Additional details about the operation
    """
    audit_log = {
        "service_name": service_name,
        "endpoint": endpoint,
        "status": status,
        "user": user,
        "details": details
    }

    # Replace with the actual Security Service's logging endpoint
    security_service_url = os.getenv("SECURITY_SERVICE_URL", "http://localhost:5005/audit-log")

    try:
        response = requests.post(security_service_url, json=audit_log)
        if response.status_code == 201:
            logging.info(f"Audit log sent successfully: {audit_log}")
        else:
            logging.error(f"Failed to send audit log: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error connecting to Security Service: {e}")

# Encryption Function
def encrypt_data(data):
    """
    Encrypts the given data using Fernet symmetric encryption.

    :param data: Data to encrypt (string)
    :return: Encrypted data (string)
    """
    if data is None:
        return None
    try:
        encrypted_data = cipher_suite.encrypt(data.encode()).decode()
        return encrypted_data
    except Exception as e:
        logging.error(f"Encryption error: {e}")
        raise e

# Decryption Function
def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using Fernet symmetric encryption.

    :param encrypted_data: Data to decrypt (string)
    :return: Decrypted data (string)
    """
    if encrypted_data is None:
        return None
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()
        return decrypted_data
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        raise e
