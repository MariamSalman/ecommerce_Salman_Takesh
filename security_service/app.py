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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///audit_logs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RATELIMIT_STORAGE_URI'] = "redis://localhost:6379"  # Redis storage URI

# Configure Limiter
limiter.init_app(app)

# Initialize extensions
db.init_app(app)
api.init_app(app)

# Configure logging
logging.basicConfig(
    filename="security_service.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    return jsonify(error="Rate limit exceeded. Please try again later."), 429

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
        logging.info("Security Service initialized and database created.")
    app.run(debug=True, port=5005)
