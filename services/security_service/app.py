from flask import Flask, jsonify
from database import db
from routes import api
from extensions import limiter
import logging
import redis
from flask_limiter.util import get_remote_address

# Initialize Flask application
app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///audit_logs.db'  # Database URI for audit logs storage
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disables modification tracking for performance reasons
app.config['RATELIMIT_STORAGE_URI'] = "redis://localhost:6379"  # Redis storage URI for rate limiter data

# Configure Limiter
limiter.init_app(app)  # Initialize Flask-Limiter with the app for rate limiting

# Initialize extensions
db.init_app(app)  # Initialize the database with Flask
api.init_app(app)  # Initialize API routes with Flask

# Configure logging
logging.basicConfig(
    filename="security_service.log",  # Set log file name for audit logs
    level=logging.INFO,  # Set log level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s"  # Set log format with timestamp, log level, and message
)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    """
    Error handler for when the rate limit is exceeded.

    Returns:
        jsonify: A JSON response with the error message and HTTP status 429.
    """
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

if __name__ == "__main__":
    """
    Main entry point of the Security Service.

    This block sets up the database and runs the Flask application on port 5005.
    The database tables are created if they do not exist when the app starts.
    """
    with app.app_context():
        db.create_all()  # Create database tables if they don't already exist
        logging.info("Security Service initialized and database created.")  # Log the initialization
    app.run(debug=True, port=5005)  # Start the Flask application in debug mode on port 5005
