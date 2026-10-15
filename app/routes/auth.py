from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from app import get_db, hash_password, verify_password
import sqlite3 

auth_bp = Blueprint("auth", __name__, url_prefix="")

# your /login and /register routes will move here soon

@auth_bp.route("/login", methods = ["POST"])
def login():
        data = request.get_json() or {}

        username = data.get("username", "").strip()
        password = data.get("password", "")

        # Missing fields → 400
        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        db = get_db()

        # ⬇️ Now also select role
        cur = db.execute(
            "SELECT id, username, email, password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()

        # Username not found or password wrong → 401
        if row is None or not check_password_hash(row["password_hash"], password):
            return jsonify({"error": "invalid credentials"}), 401

        # ✅ At this point, the user is AUTHENTICATED.
        user_id = row["id"]
        username = row["username"]
        role = row["role"]  # ⬅️ read role from DB

        # Build the JWT payload (the "badge" they carry)
        payload = {
            "user_id": user_id,
            "username": username,
            "role": role,  # ⬅️ include role in the token
            "exp": datetime.utcnow() + timedelta(hours=2),
        }

        # 🔑 Get settings from config (NOT globals)
        secret = current_app.config["JWT_SECRET"]
        algorithm = current_app.config["JWT_ALGORITHM"]

        # Sign the token with our secret + algorithm from config
        token = jwt.encode(payload, secret, algorithm=algorithm)

        # Send back token on success
        return jsonify({
            "message": "login successful",
            "token": token,
        }), 200


@auth_bp.post("/register")
def register():
        data = request.get_json() or {}

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "")

        if not username or not email or not password:
            return jsonify({"error": "username, email, and password are required"}), 400

        db = get_db()

        password_hash = hash_password(password)

        try:
            cur = db.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            db.commit()
        except sqlite3.IntegrityError:
            return jsonify({"error": "username or email already exists"}), 409

        return jsonify({"id": cur.lastrowid, "username": username, "email": email}), 201

    

   