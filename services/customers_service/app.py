from flask import Flask, jsonify, request
from database import db
from routes import api
import requests

app = Flask(__name__)

SECURITY_SERVICE_URL = "http://security_service:5005"  # URL of the Security Service

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
api.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True, port=5001)
