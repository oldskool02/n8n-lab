# db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import List, Optional

from schemas import RecipeCreate, RecipeUpdate


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

# CREATE
def create_recipe(recipe: RecipeCreate):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        INSERT INTO recipes (title, ingredients, instructions)
        VALUES (%s, %s, %s)
        RETURNING *;
    """, (
        recipe.title,
        Json(recipe.ingredients),
        Json(recipe.instructions)
    ))

    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result


# READ ALL
def get_recipes(limit: int, offset: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM recipes
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s;
    """, (limit, offset))

    results = cur.fetchall()

    cur.close()
    conn.close()

    return results


# READ ONE
def get_recipe_by_id(recipe_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM recipes
        WHERE id = %s;
    """, (recipe_id,))

    result = cur.fetchone()

    cur.close()
    conn.close()

    return result


# UPDATE
def update_recipe(recipe_id: int, recipe: RecipeUpdate):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    fields = []
    values = []

    if recipe.title is not None:
        fields.append("title = %s")
        values.append(recipe.title)

    if recipe.ingredients is not None:
        fields.append("ingredients = %s")
        values.append(Json(recipe.ingredients))

    if recipe.instructions is not None:
        fields.append("instructions = %s")
        values.append(Json(recipe.instructions))

    if not fields:
        return None

    values.append(recipe_id)

    query = f"""
        UPDATE recipes
        SET {", ".join(fields)}
        WHERE id = %s
        RETURNING *;
    """

    cur.execute(query, tuple(values))
    result = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    return result


# DELETE
def delete_recipe(recipe_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM recipes
        WHERE id = %s;
    """, (recipe_id,))

    deleted = cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    return deleted > 0