from flask import Flask, jsonify
from database import db
from routes import api
from pybreaker import CircuitBreaker
from extensions import limiter  # Import limiter from extensions.py

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

# Initialize Rate Limiter
limiter.init_app(app)

# Initialize extensions
db.init_app(app)
api.init_app(app)

@app.errorhandler(429)
def ratelimit_exceeded(e):
    return jsonify(error="Rate limit exceeded. You are allowed {} requests.".format(app.config['RATE_LIMITS'])), 429

@app.errorhandler(Exception)
def handle_general_error(e):
    return jsonify(error="An unexpected error occurred: {}".format(str(e))), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
