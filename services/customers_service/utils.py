import requests
from cryptography.fernet import Fernet

SECURITY_SERVICE_URL = "http://security_service:5005"

def log_to_audit(service, operation, status, user=None, details=None):
    payload = {
        "service": service,
        "operation": operation,
        "status": status,
        "user": user,
        "details": details
    }
    try:
        response = requests.post(f"{SECURITY_SERVICE_URL}/audit_logs", json=payload)
        response.raise_for_status()
        print(f"Audit log successful: {response.status_code}")
    except Exception as e:
        print(f"Failed to log to security service: {e}")



def fetch_encryption_key():
    try:
        response = requests.get(f"{SECURITY_SERVICE_URL}/secure_keys/encryption_key")
        response.raise_for_status()
        key = response.json().get("key_value")
        return Fernet(key)
    except Exception as e:
        print(f"Failed to fetch encryption key: {e}")
        return None

fernet = fetch_encryption_key()

def encrypt_data(data):
    return fernet.encrypt(data.encode()).decode() if fernet else data

def decrypt_data(encrypted_data):
    return fernet.decrypt(encrypted_data.encode()).decode() if fernet else encrypted_data
