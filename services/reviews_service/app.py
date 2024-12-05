from flask import Flask
from database import db
from routes import api
from utils import log_to_audit  # Import the logging utility

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reviews.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
api.init_app(app)

# Log service initialization to the audit system
log_to_audit(
    service_name="reviews_service",
    endpoint="Initialization",
    status="success",
    details="Reviews Service has been initialized successfully"
)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True, port=5004)
