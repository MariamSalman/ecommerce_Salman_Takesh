import logging
from datetime import datetime
from cryptography.fernet import Fernet
import requests

# Initialize logging
logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Encryption key (in a real-world app, use a secure key management service)
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

# Logging function
def log_to_audit(service_name, endpoint, status, details):
    """
    Logs audit events to a file.

    :param service_name: Name of the service
    :param endpoint: API endpoint accessed
    :param status: Operation status (success, error)
    :param details: Additional details about the operation
    """
    log_entry = f"{service_name} | {endpoint} | {status} | {details}"
    logging.info(log_entry)

# Encryption utility
def encrypt_data(data):
    """
    Encrypts the provided data.

    :param data: String to encrypt
    :return: Encrypted string
    """
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode()

# Decryption utility
def decrypt_data(encrypted_data):
    """
    Decrypts the provided encrypted string.

    :param encrypted_data: Encrypted string to decrypt
    :return: Decrypted string
    """
    if not encrypted_data:
        return None
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

# Cross-service communication utility
def call_service_api(method, url, payload=None, headers=None):
    """
    Sends an API request to another service.

    :param method: HTTP method (GET, POST, PUT, DELETE)
    :param url: Full API endpoint URL
    :param payload: Data to send in the request body
    :param headers: HTTP headers
    :return: Response object
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=payload, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Log API call success
        log_to_audit(
            service_name="sales_service",
            endpoint=url,
            status="success" if response.ok else "error",
            details=f"API call with status code {response.status_code}"
        )
        return response
    except Exception as e:
        # Log API call failure
        log_to_audit(
            service_name="sales_service",
            endpoint=url,
            status="error",
            details=f"API call failed with error: {e}"
        )
        raise
