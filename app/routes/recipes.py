from flask import Blueprint, jsonify, request, g
from app import token_required
import sqlite3
from app.models import Recipe, get_recipe_by_id, update_recipe_row
from app.services.recipe_service import get_public_recipes
from app.extensions import db
from app.services.recipe_service import get_recipe_by_id_orm


recipes_bp = Blueprint("recipes", __name__, url_prefix="")

@recipes_bp.get("/recipes")
def list_recipes():
        print("DEBUG: inside list_recipes ORM version")

        recipes = Recipe.query.order_by(Recipe.id).all()

        return jsonify([
        {
            "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "user_id": recipe.user_id,
            "is_public": bool(recipe.is_public)
        }
        for recipe in recipes
    ])
       

@recipes_bp.get("/recipes/<int:recipe_id>")
def get_recipe(recipe_id):
      recipe = get_recipe_by_id_orm(recipe_id)

      if recipe is None:
          return jsonify({"error": "recipe not found"}), 404
      
      else: 
          return jsonify({
              "id": recipe.id,
            "title": recipe.title,
            "ingredients": recipe.ingredients,
            "instructions": recipe.instructions,
            "user_id": recipe.user_id,
            "is_public": bool(recipe.is_public)
              
          })
      


@recipes_bp.post("/recipes")
@token_required
def create_recipe():
    current_user_id = g.current_user["user_id"]

    data = request.get_json()

    title = data.get("title")
    ingredients = data.get("ingredients")
    instructions = data.get("instructions")
    is_public = data.get("is_public", False)

    recipe = Recipe(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
        is_public=is_public,
        user_id=current_user_id
    )

    db.session.add(recipe)
    db.session.commit()

    return jsonify({
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "user_id": recipe.user_id,
        "is_public": bool(recipe.is_public)
    }), 201


      

@recipes_bp.patch("/recipes/<int:recipe_id>")
@token_required
def update_recipe(recipe_id):

    # Get current user info from the decorator (stored on g)
    print("DEBUG: inside update_recipe", recipe_id)
    current_user_id = g.current_user["user_id"]
    current_role = g.current_user["role"]

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "a JSON body is required"}), 400

    # Load the recipe using the ORM
    row = Recipe.query.filter_by(id=recipe_id).one_or_none()

    if row is None:
        return jsonify({"error": "recipe not found"}), 404

    # Ownership OR admin check
    is_owner = (
        row.user_id is not None
        and row.user_id == current_user_id
    )
    is_admin = current_role == "admin"

    if not (is_owner or is_admin):
        return jsonify(
            {"error": "you do not have permission to modify this recipe"}
        ), 403

    # Update fields using the ORM
    if "title" in data:
        row.title = data["title"]

    if "ingredients" in data:
        row.ingredients = data["ingredients"]

    if "instructions" in data:
        row.instructions = data["instructions"]

    if "is_public" in data:
        row.is_public = bool(data["is_public"])

    if not any(
        field in data
        for field in ("title", "ingredients", "instructions", "is_public")
    ):
        return jsonify({"error": "nothing to update"}), 400

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return jsonify(
            {"error": "a recipe with that title already exists"}
        ), 409

    return jsonify({
        "id": row.id,
        "title": row.title,
        "ingredients": row.ingredients,
        "instructions": row.instructions,
        "user_id": row.user_id,
        "is_public": bool(row.is_public)
    }), 200
      
@recipes_bp.delete("/recipes/<int:recipe_id>")
@token_required
def delete_recipe(recipe_id):

    current_user_id = g.current_user["user_id"]
    current_role = g.current_user["role"]

    row = Recipe.query.filter_by(id=recipe_id).one_or_none()
    if row is None:
        return jsonify({"error": "Recipe cannot be found"}), 404
    
    is_owner = (
        row.user_id is not None
        and row.user_id == current_user_id
    )
    is_admin = current_role == "admin"

    if not (is_owner or is_admin):
        return jsonify(
            {"error": "you do not have permission to modify this recipe"}
        ), 403
    
    db.session.delete(row)
    db.session.commit()
    return jsonify({"status": "deleted"}), 200
   
    




@recipes_bp.get("/recipes/public")
@token_required
def list_public_recipes_route():
    recipes = get_public_recipes()
    return jsonify(recipes), 200



def recipe_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "ingredients": row["ingredients"],
        "instructions": row["instructions"],
        "is_public": bool(row["is_public"]),
    }