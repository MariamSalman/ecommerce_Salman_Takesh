import requests
from datetime import datetime
import logging
from pybreaker import CircuitBreaker

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

# Circuit Breaker Configuration
breaker = CircuitBreaker(fail_max=5, reset_timeout=60)

# Audit Logging Function
def log_to_audit(service_name, endpoint, status, details):
    log_entry = f"[{datetime.now()}] {service_name} - {endpoint} - {status} - {details}"
    logging.info(log_entry)

# Cross-Service API Call Helper
@breaker
def call_service_api(method, url, payload=None):
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
