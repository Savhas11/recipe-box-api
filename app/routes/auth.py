from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from app.services.auth_service import login_user
from sqlalchemy.exc import IntegrityError
from app.extensions import db, limiter
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="")




@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).one_or_none()

    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401
    
    payload = {
    "user_id": user.id,
    "username": user.username,
    "role": "user",
    "exp": datetime.utcnow() + timedelta(hours=2),
}

   

    # Get settings from config
    secret = current_app.config["JWT_SECRET"]
    algorithm = current_app.config["JWT_ALGORITHM"]

    # Sign the token
    token = jwt.encode(payload, secret, algorithm=algorithm)

    return jsonify({
        "message": "login successful",
        "token": token,
    }), 200




@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400

    password_hash = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "username or email already exists"}), 409

    return jsonify({
        "id": user.id,
        "username": username,
        "email": email
    }), 201

   