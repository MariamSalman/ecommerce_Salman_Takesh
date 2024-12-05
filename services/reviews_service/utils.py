import requests
from datetime import datetime
import logging
from pybreaker import CircuitBreaker
from cryptography.fernet import Fernet

with open("secret.key", "rb") as key_file:
    encryption_key = key_file.read()
cipher = Fernet(encryption_key)

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Circuit Breaker Configuration
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

# Audit Logging Function
def log_to_audit(service_name, endpoint, status, details):
    """
    Logs audit information to the console with a timestamp.

    Args:
        service_name (str): The name of the service making the request.
        endpoint (str): The endpoint being accessed (e.g., "POST /goods").
        status (str): The status of the operation (e.g., "success", "error").
        details (str): Additional details about the operation.
    
    Description:
        This function generates a log entry with a timestamp for each request made to an endpoint 
        and logs it using the Python logging module.
    """
    log_entry = f"[{datetime.now()}] {service_name} - {endpoint} - {status} - {details}"
    logging.info(log_entry)

# Cross-Service API Call Helper
@breaker
def call_service_api(method, url, payload=None):
    """
    Makes an HTTP request to an external service.

    Args:
        method (str): The HTTP method to use for the request (GET, POST, PUT, DELETE).
        url (str): The URL of the external service endpoint.
        payload (dict, optional): The data to send with the request (for POST/PUT methods). Defaults to None.

    Returns:
        Response: The response object from the HTTP request.

    Description:
        This function makes an HTTP request to an external service and logs the request details 
        and response status using the `log_to_audit` function. It is protected with a circuit breaker 
        to manage retries in case of failures.
    """
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=payload)
        elif method == "PUT":
            response = requests.put(url, json=payload)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError("Invalid HTTP method")

        log_to_audit("reviews_service", url, response.status_code, f"Method: {method}, Payload: {payload}")
        return response
    except requests.exceptions.RequestException as e:
        log_to_audit("reviews_service", url, "error", f"Error: {e}")
        raise

# Encryption and Decryption Functions
def encrypt_data(data):
    """
    Encrypts the given data using Fernet encryption.

    Args:
        data (str): The data to encrypt.

    Returns:
        str: The encrypted data.

    Description:
        This function encrypts the input data using the Fernet symmetric encryption algorithm. 
        The data must be converted to bytes before encryption if it's a string.
    """
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    return cipher.encrypt(data).decode('utf-8')

def decrypt_data(encrypted_data):
    """
    Decrypts the given data using Fernet encryption.

    Args:
        encrypted_data (str): The encrypted data to decrypt.

    Returns:
        str: The decrypted data.

    Description:
        This function decrypts the input encrypted data using the Fernet symmetric decryption algorithm.
        The encrypted data must be in string format.
    """
    return cipher.decrypt(encrypted_data.encode('utf-8')).decode('utf-8')
