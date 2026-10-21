from app.extensions import db


def get_recipe_by_id(db_conn, recipe_id):
    cursor = db_conn.execute(
        "SELECT * FROM recipes WHERE id = ?", (recipe_id,)
    )
    row = cursor.fetchone()
    return row


def update_recipe_row(db_conn, recipe_id, fields, values):
    values = values.copy()
    values.append(recipe_id)

    cursor = db_conn.execute(
        f"UPDATE recipes SET {', '.join(fields)} WHERE id = ?",
        values,
    )
    db_conn.commit()
    return cursor.rowcount


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password_hash = db.Column(db.String, nullable=False)


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False, unique=True)
    ingredients = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False, default="")
    is_public = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer)


