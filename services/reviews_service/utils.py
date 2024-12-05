import requests
from datetime import datetime

def log_to_audit(service_name, endpoint, status, details):
    """
    Log an action to the audit system.
    """
    log_entry = f"[{datetime.now()}] {service_name} - {endpoint} - {status} - {details}"
    # You can enhance this by writing to a file or external logging service
    print(log_entry)

def call_service_api(method, url, payload=None):
    """
    Makes a cross-service API call.
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
        return response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling {url}: {e}")
