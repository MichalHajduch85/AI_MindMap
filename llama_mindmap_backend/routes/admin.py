from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from llama_mindmap_backend.models import Log, User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).limit(100).all()
    return jsonify([{
        'user_id': str(log.user_id),
        'event_type': log.event_type,
        'event_data': log.event_data,
        'timestamp': log.timestamp.isoformat()
    } for log in logs]), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    } for user in users]), 200
