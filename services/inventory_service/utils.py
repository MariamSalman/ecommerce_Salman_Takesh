import requests
from cryptography.fernet import Fernet
import os
import logging
from pybreaker import CircuitBreaker

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)
breaker = circuit_breaker

# Logging Function
def log_to_audit(service_name, endpoint, status, user=None, details=""):
    """
    Logs audit information to a remote security service.

    Args:
        service_name (str): The name of the service making the request.
        endpoint (str): The endpoint being accessed (e.g., "POST /goods").
        status (str): The status of the operation (e.g., "success", "error").
        user (str, optional): The user performing the action (e.g., username). Default is None.
        details (str, optional): Additional details about the operation. Default is an empty string.
    
    Description:
        This function creates an audit log and sends it as a JSON payload to the security service.
        If the request to the security service fails, it retries based on the CircuitBreaker configuration.
        All errors in the process are logged.
    """
    audit_log = {
        "service_name": service_name,
        "endpoint": endpoint,
        "status": status,
        "user": user,
        "details": details
    }
    security_service_url = os.getenv("SECURITY_SERVICE_URL", "http://localhost:5005/audit-log")

    @circuit_breaker
    def send_audit_log():
        try:
            response = requests.post(security_service_url, json=audit_log)
            if response.status_code == 201:
                logging.info(f"Audit log sent successfully: {audit_log}")
            else:
                logging.error(f"Failed to send audit log: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to Security Service: {e}")
            raise e

    try:
        send_audit_log()
    except Exception as e:
        logging.error(f"Audit log failed due to circuit breaker: {e}")

# Encryption Function
def encrypt_data(data):
    """
    Encrypts data using the provided encryption key.

    Args:
        data (str): The data to be encrypted.
    
    Returns:
        str: The encrypted data as a string.
    
    Description:
        This function encrypts the provided data using the Fernet encryption scheme and returns the 
        encrypted data as a string. If the data is `None`, it returns `None`.
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
    Decrypts data using the provided decryption key.

    Args:
        encrypted_data (str): The encrypted data to be decrypted.
    
    Returns:
        str: The decrypted data as a string.
    
    Description:
        This function decrypts the provided encrypted data using the Fernet decryption scheme and returns 
        the decrypted data as a string. If the data is `None`, it returns `None`.
    """
    if encrypted_data is None:
        return None
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()
        return decrypted_data
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        raise e
