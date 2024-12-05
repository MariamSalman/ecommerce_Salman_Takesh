from database import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    service = db.Column(db.String(80), nullable=False)  # E.g., "customers_service"
    operation = db.Column(db.String(80), nullable=False)  # E.g., "POST /register"
    status = db.Column(db.String(20), nullable=False)  # E.g., "success", "error"
    user = db.Column(db.String(80), nullable=True)  # Username if applicable
    details = db.Column(db.String(255), nullable=True)  # Error or request details

class SecureKey(db.Model):
    __tablename__ = 'secure_keys'
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(80), unique=True, nullable=False)
    key_value = db.Column(db.String(255), nullable=False)  # Encrypted key
