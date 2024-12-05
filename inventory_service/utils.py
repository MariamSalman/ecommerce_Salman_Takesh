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
    if encrypted_data is None:
        return None
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode()).decode()
        return decrypted_data
    except Exception as e:
        logging.error(f"Decryption error: {e}")
        raise e
