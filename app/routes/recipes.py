from flask import Blueprint, jsonify, request, g
from app import get_db, recipe_to_dict, token_required
import sqlite3

recipes_bp = Blueprint("recipes", __name__, url_prefix="")

recipes_bp = Blueprint("recipes", __name__, url_prefix="")

@recipes_bp.get("/recipes")
def list_recipes():
        rows = get_db().execute("SELECT * FROM recipes ORDER BY id").fetchall()
        return jsonify([recipe_to_dict(r) for r in rows])

@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
        row = get_db().execute(
            "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
        ).fetchone()
        if row is None:
            return jsonify({"error": "recipe not found"}), 404
        return jsonify(recipe_to_dict(row))

@recipes_bp.patch("/recipes/<int:recipe_id>")
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

@recipes_bp.delete("/recipes/<int:recipe_id>")
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