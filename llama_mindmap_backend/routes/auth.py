from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from llama_mindmap_backend.extensions import db
from llama_mindmap_backend.models import User, Log
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import uuid
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Valid password"

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: user_data
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              minLength: 3
              maxLength: 80
            email:
              type: string
              format: email
            password:
              type: string
              minLength: 6
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            message:
              type: string
            user_id:
              type: string
      400:
        description: Validation error
        schema:
          type: object
          properties:
            message:
              type: string
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'message': f'{field.title()} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate username
        if len(username) < 3 or len(username) > 80:
            return jsonify({'message': 'Username must be between 3 and 80 characters'}), 400
        
        # Validate email
        if not validate_email(email):
            return jsonify({'message': 'Invalid email format'}), 400
        
        # Validate password
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'Email already registered'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already taken'}), 400
        
        # Create new user
        user_id = uuid.uuid4()
        new_user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Log the registration
        log = Log(
            user_id=user_id,
            event_type='user_registered',
            event_data={'username': username, 'email': email}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': str(user_id)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: credentials
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
            password:
              type: string
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            user:
              type: object
              properties:
                id:
                  type: string
                username:
                  type: string
                email:
                  type: string
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            message:
              type: string
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        if 'email' not in data or 'password' not in data:
            return jsonify({'message': 'Email and password are required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        # Log the login
        log = Log(
            user_id=user.id,
            event_type='user_login',
            event_data={'email': email}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed. Please try again.'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get user profile
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    responses:
      200:
        description: User profile
        schema:
          type: object
          properties:
            id:
              type: string
            username:
              type: string
            email:
              type: string
            profile_data:
              type: object
            created_at:
              type: string
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'profile_data': user.profile_data,
            'created_at': user.created_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update user profile
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: profile_data
        schema:
          type: object
          properties:
            username:
              type: string
            profile_data:
              type: object
    responses:
      200:
        description: Profile updated successfully
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update username if provided
        if 'username' in data:
            new_username = data['username'].strip()
            if len(new_username) < 3 or len(new_username) > 80:
                return jsonify({'message': 'Username must be between 3 and 80 characters'}), 400
            
            # Check if username is already taken by another user
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'message': 'Username already taken'}), 400
            
            user.username = new_username
        
        # Update profile data if provided
        if 'profile_data' in data:
            user.profile_data = data['profile_data']
        
        db.session.commit()
        
        # Log the update
        log = Log(
            user_id=user_id,
            event_type='profile_updated',
            event_data={'updated_fields': list(data.keys())}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Change user password
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: password_data
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
            new_password:
              type: string
    responses:
      200:
        description: Password changed successfully
    """
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({'message': 'Current password and new password are required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'message': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'message': message}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        # Log the password change
        log = Log(
            user_id=user_id,
            event_type='password_changed',
            event_data={'timestamp': datetime.utcnow().isoformat()}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to change password'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    User logout (mainly for logging purposes)
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    responses:
      200:
        description: Logout successful
    """
    try:
        user_id = get_jwt_identity()
        
        # Log the logout
        log = Log(
            user_id=user_id,
            event_type='user_logout',
            event_data={'timestamp': datetime.utcnow().isoformat()}
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Logout successful'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Logout completed'}), 200