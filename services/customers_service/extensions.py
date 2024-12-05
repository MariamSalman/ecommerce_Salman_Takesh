from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)

"""
The `limiter` object is an instance of `Limiter` used for rate limiting in a Flask application.

Rate limiting is a technique used to control the rate at which clients can access certain resources or endpoints. The `limiter` is used to prevent abuse or overuse of resources by restricting the number of requests a client can make within a certain time period.

Usage:
- The `limiter` object is typically initialized with a `key_func` that determines how to identify the client making the request. In this case, `get_remote_address` is used, which retrieves the client's IP address.

Key features:
1. Rate limits can be applied to specific routes or globally.
2. The `key_func` argument specifies how to identify unique clients (e.g., by IP address, user ID, etc.).
3. It works with Flask’s request lifecycle to limit access based on the configuration.

Example:
- By default, rate limits are applied globally, but you can specify rate limits for individual routes using the `@limiter.limit` decorator.

Example usage:
    - `@limiter.limit("200 per day")` can be used to apply a rate limit of 200 requests per day for a specific route.
    - `limiter.init_app(app)` should be called to initialize the limiter in the Flask application context.
"""
