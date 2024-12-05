from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Limiter with the key function to identify users based on their IP address
limiter = Limiter(key_func=get_remote_address)

"""
The `limiter` object is an instance of `Flask-Limiter`, used to apply rate limits on API endpoints in a Flask application.

The `Flask-Limiter` extension provides easy-to-use rate-limiting functionality that restricts the number of requests a client can make 
to the API over a specific time period (e.g., 100 requests per hour). This helps protect the server from abuse and ensures fair use of resources.

How it works:

1. **Key Function (`key_func`)**:
   - The `key_func` specifies how the client (user) is identified for rate limiting. In this case, `get_remote_address` is used, which gets the IP address of the client making the request.

2. **Rate Limiting**:
   - The `limiter` object is used to define the rate limits for specific endpoints.
   - You can set limits like "200 per day" or "50 per hour", which will restrict how many requests a client can make in those timeframes.

### Example Usage:

1. **Limit a single endpoint**:
   - You can apply a rate limit to a specific endpoint using the `@limiter.limit` decorator.

```python
@app.route('/api/resource')
@limiter.limit("5 per minute")  # Allow 5 requests per minute per client
def resource():
    return "This is a rate-limited resource."
