from flask import Flask, jsonify
from database import db
from routes import api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pybreaker import CircuitBreaker

# Flask App Initialization
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CIRCUIT_BREAKER_FAIL_MAX'] = 5
app.config['CIRCUIT_BREAKER_RESET_TIMEOUT'] = 60
app.config['RATE_LIMITS'] = ["200 per day", "50 per hour"]

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(
    fail_max=app.config['CIRCUIT_BREAKER_FAIL_MAX'], 
    reset_timeout=app.config['CIRCUIT_BREAKER_RESET_TIMEOUT']
)

# Rate Limiter Configuration
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=app.config['RATE_LIMITS']
)

# Initialize extensions
db.init_app(app)
api.init_app(app)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    """
    Handles rate limit exceeded errors (HTTP 429).

    This function is triggered when the rate limit for the API is exceeded. It returns a JSON response
    with a relevant error message and the rate limit information.

    Args:
        e (Exception): The error raised when the rate limit is exceeded.

    Returns:
        Response: A JSON response indicating rate limit error.
    """
    return jsonify(error="Rate limit exceeded. You are allowed {} requests.".format(app.config['RATE_LIMITS'])), 429

@app.errorhandler(Exception)
def handle_general_error(e):
    """
    Handles general errors that occur during the request (HTTP 500).

    This function catches all other exceptions and returns a generic error message indicating an unexpected error
    during the application runtime.

    Args:
        e (Exception): The exception raised during the application runtime.

    Returns:
        Response: A JSON response indicating a general internal server error.
    """
    return jsonify(error="An unexpected error occurred: {}".format(str(e))), 500

if __name__ == "__main__":
    """
    Initializes the Flask app and runs it.

    This block sets up the database, creates all necessary tables, and starts the Flask server 
    on port 5003 in debug mode.

    Args:
        None

    Returns:
        None
    """
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True, port=5003)