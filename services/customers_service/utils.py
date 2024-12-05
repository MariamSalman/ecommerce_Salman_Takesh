import requests
from cryptography.fernet import Fernet
from pybreaker import CircuitBreaker

# Configuration for the security service URL
SECURITY_SERVICE_URL = "http://127.0.0.1:5005"

# Circuit breaker to handle retries and failures
circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

def log_to_audit(service, operation, status, user=None, details=None):
    """
    Logs an audit entry to the security service.

    This function sends a JSON payload to the security service's `/audit_logs` endpoint.
    It logs details about operations performed in the service, including status and user information.

    Args:
        service (str): The name of the service (e.g., "customers_service").
        operation (str): The operation being performed (e.g., "POST /customers/register").
        status (str): The status of the operation (e.g., "success", "error").
        user (str, optional): The username of the user performing the operation.
        details (str, optional): Additional information about the operation.

    Returns:
        None
    """
    payload = {
        "service": service,
        "operation": operation,
        "status": status,
        "user": user,
        "details": details
    }
    try:
        response = circuit_breaker.call(requests.post, f"{SECURITY_SERVICE_URL}/audit_logs", json=payload)
        response.raise_for_status()
        print(f"Audit log successful: {response.status_code}")
    except Exception as e:
        print(f"Failed to log to security service: {e}. Details: {payload}")

def fetch_encryption_key():
    """
    Fetches the encryption key from the security service.

    This function retrieves the encryption key from the security service's `/secure_keys/encryption_key` endpoint.
    It uses a circuit breaker to handle retries and failures.

    Returns:
        Fernet: An instance of Fernet initialized with the encryption key.
        None: If the key retrieval fails.
    """
    try:
        response = circuit_breaker.call(requests.get, f"{SECURITY_SERVICE_URL}/secure_keys/encryption_key")
        response.raise_for_status()
        key = response.json().get("key_value")
        return Fernet(key)
    except Exception as e:
        print(f"Failed to fetch encryption key: {e}")
        return None

# Initialize the encryption utility with the fetched key
fernet = fetch_encryption_key()

def encrypt_data(data):
    """
    Encrypts the given data using the fetched encryption key.

    Args:
        data (str): The plain text data to be encrypted.

    Returns:
        str: The encrypted data in string format.
        str: Returns the plain text data if the encryption key is not available.
    """
    return fernet.encrypt(data.encode()).decode() if fernet else data

def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using the fetched encryption key.

    Args:
        encrypted_data (str): The encrypted data to be decrypted.

    Returns:
        str: The decrypted plain text data.
        str: Returns the encrypted data as is if the encryption key is not available.
    """
    return fernet.decrypt(encrypted_data.encode()).decode() if fernet else encrypted_data
