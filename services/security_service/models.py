from database import db
from datetime import datetime

# AuditLog Model: Tracks service operations and logs for auditing purposes.
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'  # The table name in the database

    # Define columns in the 'audit_logs' table
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the log entry
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Timestamp of the log entry
    service = db.Column(db.String(80), nullable=False)  # Name of the service (e.g., "customers_service")
    operation = db.Column(db.String(80), nullable=False)  # The operation being logged (e.g., "POST /register")
    status = db.Column(db.String(20), nullable=False)  # Status of the operation (e.g., "success", "error")
    user = db.Column(db.String(80), nullable=True)  # Username involved in the operation (nullable if not applicable)
    details = db.Column(db.String(255), nullable=True)  # Additional details or error messages (nullable)

    def __repr__(self):
        return f"<AuditLog id={self.id}, service={self.service}, operation={self.operation}, status={self.status}, user={self.user}>"

    """
    This model is used to store audit logs for each operation performed in the service.
    It tracks the timestamp, service name, operation details, status, user (if applicable), and any relevant details.
    """

# SecureKey Model: Stores encrypted keys for secure operations.
class SecureKey(db.Model):
    __tablename__ = 'secure_keys'  # The table name in the database

    # Define columns in the 'secure_keys' table
    id = db.Column(db.Integer, primary_key=True)  # Primary key for the secure key record
    key_name = db.Column(db.String(80), unique=True, nullable=False)  # Name of the key (unique)
    key_value = db.Column(db.String(255), nullable=False)  # Encrypted value of the key

    def __repr__(self):
        return f"<SecureKey id={self.id}, key_name={self.key_name}>"

    """
    This model stores encrypted keys used for secure operations within the application.
    The `key_name` is unique, ensuring that each key is identifiable. The `key_value` contains the encrypted key.
    """

