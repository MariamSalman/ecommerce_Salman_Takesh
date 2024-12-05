import logging
from cryptography.fernet import Fernet
import requests
from pybreaker import CircuitBreaker

# Initialize logging
logging.basicConfig(
    filename="audit.log",  # Log to a file named 'audit.log'
    level=logging.INFO,  # Set logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s"  # Define log entry format
)

# Encryption key
ENCRYPTION_KEY = Fernet.generate_key()  # Generate a new Fernet encryption key
cipher_suite = Fernet(ENCRYPTION_KEY)  # Initialize the cipher suite for encryption/decryption

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)  # Configure the circuit breaker with a max of 5 failures and a 60-second reset timeout

# Logging Function
def log_to_audit(service_name, endpoint, status, details):
    """
    Logs audit information for each request made to the service.

    Args:
        service_name (str): The name of the service making the request.
        endpoint (str): The endpoint being accessed.
        status (str): The status of the request (e.g., 'success', 'error').
        details (str): Additional details about the request (e.g., error message or success information).

    Returns:
        None
    """
    log_entry = f"{service_name} | {endpoint} | {status} | {details}"  # Format the log entry
    logging.info(log_entry)  # Log the entry to the file

# Encryption Utility
def encrypt_data(data):
    """
    Encrypts the given data using the Fernet encryption suite.

    Args:
        data (str): The plaintext string to be encrypted.

    Returns:
        str: The encrypted string.
    """
    if not data:
        return None  # Return None if no data is provided
    return cipher_suite.encrypt(data.encode()).decode()  # Encrypt and return as a string

# Decryption Utility
def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using the Fernet decryption suite.

    Args:
        encrypted_data (str): The encrypted string to be decrypted.

    Returns:
        str: The decrypted string.
    """
    if not encrypted_data:
        return None  # Return None if no encrypted data is provided
    return cipher_suite.decrypt(encrypted_data.encode()).decode()  # Decrypt and return as a string

# Cross-Service API Call
@breaker
def call_service_api(method, url, payload=None, headers=None):
    """
    Makes an HTTP request to another service using the specified HTTP method.

    Args:
        method (str): The HTTP method to be used (GET, POST, PUT, DELETE).
        url (str): The URL of the service endpoint.
        payload (dict, optional): The data to be sent with the request (for POST/PUT).
        headers (dict, optional): Additional headers to be included in the request.

    Returns:
        Response: The response object returned by the requests library.
    
    Raises:
        Exception: If the request fails, an error is logged and the exception is raised.
    """
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)  # Perform a GET request
        elif method.upper() == "POST":
            response = requests.post(url, json=payload, headers=headers)  # Perform a POST request with JSON payload
        elif method.upper() == "PUT":
            response = requests.put(url, json=payload, headers=headers)  # Perform a PUT request with JSON payload
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)  # Perform a DELETE request
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")  # Raise an exception if the method is not supported

        # Log the response details
        log_to_audit(
            service_name="sales_service",  # Name of the service making the request
            endpoint=url,  # The endpoint that was accessed
            status="success" if response.ok else "error",  # Log success or error based on response status
            details=f"API call with status code {response.status_code}"  # Include the status code in the details
        )
        return response  # Return the response object

    except Exception as e:
        # Log the exception if the request fails
        log_to_audit(
            service_name="sales_service",  # Name of the service making the request
            endpoint=url,  # The endpoint that was accessed
            status="error",  # Status is 'error' because the request failed
            details=f"API call failed with error: {e}"  # Log the error message
        )
        raise  # Re-raise the exception to propagate it further
