from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)

"""
The `limiter` object is an instance of `Flask-Limiter` used for rate limiting requests in a Flask application.

Rate limiting is a technique to control the rate at which clients can access a service, helping to prevent abuse and overuse of resources.

Usage:
- The `limiter` object is initialized with a `key_func` that determines the client identity (in this case, the client's IP address using `get_remote_address`).
- The rate limiting is applied on a per-client basis, limiting how many requests a client (identified by their IP) can make in a given time window.

Key Features:
1. Rate limits can be defined globally or for specific routes.
2. The `key_func` argument specifies how to identify unique clients (e.g., by IP address, user ID, etc.).
3. It works with Flask’s request lifecycle to limit access based on the provided configuration.

Example Usage:
    - `@limiter.limit("200 per day")` applies a rate limit of 200 requests per day per IP address for a specific route.
    - `limiter.init_app(app)` initializes the rate limiter within the Flask app context.

The `Flask-Limiter` library provides decorators and functions to apply these limits easily to your routes.
"""
