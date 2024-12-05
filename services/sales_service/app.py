from flask import Flask
from database import db
from routes import api
from utils import log_to_audit  # Import logging utility

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
api.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables

        # Log service initialization
        log_to_audit(
            service_name="sales_service",
            endpoint="startup",
            status="success",
            details="Sales service initialized and database created"
        )
    app.run(debug=True, port=5003)
