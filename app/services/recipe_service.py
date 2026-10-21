
from app.models import Recipe


def recipe_to_dict(recipe):
    return {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": recipe.ingredients,
        "instructions": recipe.instructions,
        "user_id": recipe.user_id,
        "is_public": bool(recipe.is_public),
    }


def get_public_recipes():
    recipes = (
        Recipe.query
        .filter_by(is_public=True)
        .order_by(Recipe.id)
        .all()
    )
    return [recipe_to_dict(recipe) for recipe in recipes]


def get_recipe_by_id_orm(recipe_id):
    recipe = (
        Recipe.query
        .filter_by(id=recipe_id)
        .one_or_none()
    )
    return recipe
