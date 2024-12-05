from flask_restful import Api, Resource
from models import AuditLog, SecureKey
from database import db
from flask import request, jsonify

api = Api()

class AuditLogsAPI(Resource):
    def get(self):
        logs = AuditLog.query.all()
        return jsonify([{
            'id': log.id,
            'timestamp': log.timestamp,
            'service': log.service,
            'operation': log.operation,
            'status': log.status,
            'user': log.user,
            'details': log.details
        } for log in logs])

    def post(self):
        data = request.json
        log = AuditLog(
            service=data.get('service'),
            operation=data.get('operation'),
            status=data.get('status'),
            user=data.get('user'),
            details=data.get('details')
        )
        db.session.add(log)
        db.session.commit()
        return {"message": "Log added successfully"}, 201

class SecureKeysAPI(Resource):
    def post(self):
        data = request.json
        key_name = data.get('key_name')
        key_value = data.get('key_value')  # This should be encrypted
        key = SecureKey(key_name=key_name, key_value=key_value)
        db.session.add(key)
        db.session.commit()
        return {"message": "Key stored successfully"}, 201

    def get(self, key_name):
        key = SecureKey.query.filter_by(key_name=key_name).first()
        if not key:
            return {"error": "Key not found"}, 404
        return {"key_value": key.key_value}  # Decrypt before returning

api.add_resource(AuditLogsAPI, '/audit_logs')
api.add_resource(SecureKeysAPI, '/secure_keys', '/secure_keys/<string:key_name>')
