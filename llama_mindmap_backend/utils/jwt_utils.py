from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import jsonify

def get_current_user_id():
    return get_jwt_identity()

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        # Add logic to verify if user_id belongs to an admin
        # For now, assume all users are allowed
        return fn(*args, **kwargs)
    return wrapper
