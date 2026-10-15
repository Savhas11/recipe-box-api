"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""

import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, g, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.config import DevelopmentConfig, TestingConfig, ProductionConfig



def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing or invalid authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        secret = current_app.config["JWT_SECRET"]

        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
        except ExpiredSignatureError:
            return jsonify({"error": "token expired – please log in again"}), 401
        except InvalidTokenError:
            return jsonify({"error": "invalid token"}), 401

        # ✅ Save the user info for the route to use
        g.current_user = {
            "user_id": payload["user_id"],
            "role": payload.get("role", "user")
        }

        # 👉 now call the original route
        return f(*args, **kwargs)

    return wrapper

def get_db():
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


# app = Flask(__name__)

def create_app(config_name):
    app = Flask(__name__)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.routes.recipes import recipes_bp
    app.register_blueprint(recipes_bp)

    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    @app.teardown_appcontext
    def close_db(exception):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @app.get("/")
    def hello():
        return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})

    return app

def hash_password(plain_password: str) -> str:
    """Turn a plain password into a one-way hash for storing in the database."""
    return generate_password_hash(plain_password)


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Check if a candidate password matches the stored hash."""
    return check_password_hash(stored_hash, candidate_password)







def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }



