from flask import Flask, jsonify
from database import db
from routes import api
from extensions import limiter  # Import limiter from extensions.py
from pybreaker import CircuitBreaker

# Flask App Initialization
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CIRCUIT_BREAKER_FAIL_MAX'] = 5
app.config['CIRCUIT_BREAKER_RESET_TIMEOUT'] = 60
app.config['RATE_LIMITS'] = ["200 per day", "50 per hour"]

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(
    fail_max=app.config['CIRCUIT_BREAKER_FAIL_MAX'], 
    reset_timeout=app.config['CIRCUIT_BREAKER_RESET_TIMEOUT']
)

# Initialize extensions
limiter.init_app(app)  # Initialize limiter
db.init_app(app)
api.init_app(app)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    """
    Handles the rate limit exceeded error (HTTP 429).

    This function returns a JSON response indicating that the rate limit has been exceeded 
    and provides the rate limit information from the configuration.

    Args:
        e (Exception): The error raised when the rate limit is exceeded.

    Returns:
        Response: JSON response indicating the rate limit error.
    """
    return jsonify(error="Rate limit exceeded. You are allowed {} requests.".format(app.config['RATE_LIMITS'])), 429

@app.errorhandler(Exception)
def handle_general_error(e):
    """
    Handles general errors that occur during the request (HTTP 500).

    This function returns a JSON response indicating an unexpected error has occurred 
    during the application runtime.

    Args:
        e (Exception): The exception raised during the application runtime.

    Returns:
        Response: JSON response indicating a general internal server error.
    """
    return jsonify(error="An unexpected error occurred: {}".format(str(e))), 500

if __name__ == "__main__":
    """
    Initializes the Flask app and runs it.

    This block sets up the database, creates all necessary tables, and starts the Flask server 
    on port 5002 in debug mode.

    Args:
        None

    Returns:
        None
    """
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True, port=5002)
