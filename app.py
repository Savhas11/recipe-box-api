"""Recipe Box API — BE104 course skeleton.

A working Flask + SQLite CRUD API for recipes. It stores data perfectly —
and it trusts everyone. There is no authentication and no authorization yet.
That is the point: you will add both, lesson by lesson, in Units 2 and 3.
"""

import sqlite3
import os

from dotenv import load_dotenv
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timedelta

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")

from flask import Flask, g, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from functools import wraps
import os
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "missing or invalid authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        secret = os.getenv("JWT_SECRET")

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

DATABASE = "recipes.db"

app = Flask(__name__)

def hash_password(plain_password: str) -> str:
    """Turn a plain password into a one-way hash for storing in the database."""
    return generate_password_hash(plain_password)


def verify_password(stored_hash: str, candidate_password: str) -> bool:
    """Check if a candidate password matches the stored hash."""
    return check_password_hash(stored_hash, candidate_password)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }


@app.get("/")
def hello():
    return jsonify({"message": "Recipe Box API", "recipes": "/recipes"})


@app.get("/recipes")
def list_recipes():
    rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
    return jsonify([recipe_to_dict(r) for r in rows])

@app.post("/register")
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

@app.post("/login")
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

    # Sign the token with our secret
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # Send back token on success
    return jsonify({
        "message": "login successful",
        "token": token,
    }), 200

@app.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
    row = get_db().execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    if row is None:
        return jsonify({"error": "recipe not found"}), 404
    return jsonify(recipe_to_dict(row))

@app.patch("/recipes/<int:recipe_id>")
@token_required
def update_recipe(recipe_id):
    # 🧍 get current user info from the decorator (stored on g)
    current_user_id = g.current_user["user_id"]
    current_role = g.current_user["role"]

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    db = get_db()

    # Load the recipe from the DB
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    # 🔒 Ownership OR admin check
    is_owner = (row["user_id"] is not None and row["user_id"] == current_user_id)
    is_admin = (current_role == "admin")

    if not (is_owner or is_admin):
        return jsonify(
            {"error": "you do not have permission to modify this recipe"}
        ), 403

    # 👉 If we get here, user IS owner or admin – safe to update
    fields, values = [], []
    for column in ("title", "ingredients", "instructions"):
        if column in data:
            fields.append(f"{column} = ?")
            values.append(data[column])
    if "is_public" in data:
        fields.append("is_public = ?")
        values.append(1 if data["is_public"] else 0)
    if not fields:
        return jsonify({"error": "nothing to update"}), 400

    values.append(recipe_id)

    try:
        cur = db.execute(
            f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?", values
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "a recipe with that title already exists"}), 409

    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404

    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()
    return jsonify(recipe_to_dict(row)), 200


@app.delete("/recipes/<int:recipe_id>")
@token_required
def delete_recipe(recipe_id):
    # 🧍 get current user info from decorator
    current_user_id = g.current_user["user_id"]
    current_role = g.current_user["role"]

    db = get_db()

    # 🔒 Load the recipe to check ownership
    row = db.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    ).fetchone()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    # 🔒 Ownership OR admin check
    is_owner = (row["user_id"] is not None and row["user_id"] == current_user_id)
    is_admin = (current_role == "admin")

    if not (is_owner or is_admin):
        return jsonify(
            {"error": "you do not have permission to delete this recipe"}
        ), 403

    # ✅ User is owner or admin – safe to delete
    cur = db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()

    if cur.rowcount == 0:
        return jsonify({"error": "recipe not found"}), 404

    return jsonify({"message": "recipe deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
