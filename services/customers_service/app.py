from flask import Flask, jsonify
from database import db
from routes import api
from pybreaker import CircuitBreaker
from extensions import limiter  # Import limiter from extensions.py

# Flask App Initialization
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CIRCUIT_BREAKER_FAIL_MAX'] = 5
app.config['CIRCUIT_BREAKER_RESET_TIMEOUT'] = 60
app.config['RATE_LIMITS'] = ["200 per day", "50 per hour"]

# Circuit Breaker Configuration
circuit_breaker = CircuitBreaker(
    fail_max=app.config['CIRCUIT_BREAKER_FAIL_MAX'], 
    reset_timeout=app.config['CIRCUIT_BREAKER_RESET_TIMEOUT']
)

limiter.init_app(app)

# Initialize extensions
db.init_app(app)
api.init_app(app)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    """
    Handle rate limit exceeded error.

    This function is triggered when the rate limit for the API is exceeded.
    It returns a JSON response with a relevant error message and the rate limit information.

    Args:
        e (Exception): The error raised when the rate limit is exceeded.

    Returns:
        Response: A JSON response indicating rate limit error.
    """
    return jsonify(error="Rate limit exceeded. You are allowed {} requests.".format(app.config['RATE_LIMITS'])), 429

@app.errorhandler(Exception)
def handle_general_error(e):
    """
    Handle general errors that occur during the request.

    This function is triggered for any unexpected errors that occur during 
    the API execution, providing a generic error message.

    Args:
        e (Exception): The exception raised during the application runtime.

    Returns:
        Response: A JSON response indicating an internal server error.
    """
    return jsonify(error="An unexpected error occurred: {}".format(str(e))), 500

if __name__ == "__main__":
    """
    Initialize the Flask app and run it.

    This block sets up the database and runs the Flask server in debug mode on port 5001.
    The database tables are created if they do not exist.

    Args:
        None

    Returns:
        None
    """
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True, port=5001)
