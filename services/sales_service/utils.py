import logging
from cryptography.fernet import Fernet
import requests
from pybreaker import CircuitBreaker
import os

# Initialize logging
logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Encryption Key Configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY is not set or invalid.")
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

# Logging Function
def log_to_audit(service_name, endpoint, status, details):
    log_entry = f"{service_name} | {endpoint} | {status} | {details}"
    logging.info(log_entry)

# Encryption Utility
def encrypt_data(data):
    if not data:
        return None
    try:
        return cipher_suite.encrypt(data.encode()).decode()
    except Exception as e:
        logging.error(f"Encryption failed: {e}")
        raise

# Decryption Utility
def decrypt_data(encrypted_data):
    if not encrypted_data:
        return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        raise

# Cross-Service API Call with Circuit Breaker
@circuit_breaker
def call_service_api(method, url, payload=None, headers=None):
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

        log_to_audit(
            service_name="sales_service",
            endpoint=url,
            status="success" if response.ok else "error",
            details=f"API call with status code {response.status_code}"
        )
        return response
    except Exception as e:
        log_to_audit(
            service_name="sales_service",
            endpoint=url,
            status="error",
            details=f"API call failed with error: {e}"
        )
        raise
