from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import request, jsonify
from werkzeug.security import check_password_hash
from models.user import User  # Assuming the User model is in models/user.py

# JWT Setup
jwt = JWTManager()

# Login route: Validate user credentials and return JWT token
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Validate username and password
    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    # Find the user by username
    user = User.objects(username=username).first()

    # Validate the user and password
    if user and check_password_hash(user.password, password):  # Use check_password_hash
        token = create_jwt_token(user.username)
        return jsonify(access_token=token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

# Function to create JWT token
def create_jwt_token(user_id):
    return create_access_token(identity=user_id)
