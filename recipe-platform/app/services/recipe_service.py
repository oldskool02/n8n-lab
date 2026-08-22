from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Recipe, RecipeIngredient, RecipeStep
from app.schemas import RecipeCreate


def get_user_recipes(db: Session, user_id: int):
    """
    Get all recipes for a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (int): ID of the user.

    """

    statement = select(Recipe).where(
        Recipe.user_id == user_id
    )
    result = db.execute(statement)

    return result.scalars().all()


def create_recipe_service(
    db: Session,
    user_id: int,
    data: RecipeCreate,
):
    recipe = Recipe(
        user_id=user_id,
        title=data.title,
        servings=data.servings,
    )

    for item in data.ingredients:
        ingredient = RecipeIngredient(
            quantity=item.quantity,
            unit=item.unit,
            ingredient=item.ingredient,
        )

        recipe.ingredients.append(ingredient)

    for item in data.steps:
        step = RecipeStep(
            step_number=item.step_number,
            instruction=item.instruction,
        )

        recipe.steps.append(step)

    try:
        db.add(recipe)
        db.commit()
        db.refresh(recipe)

    except Exception:
        db.rollback()
        raise

    return recipe


def get_user_recipe(
    db: Session,
    user_id: int,
    recipe_id: int,
):
    """
    Get a specific recipe belonging to the user.

    Returns:
        Recipe | None: The recipe if it belongs to the user,
        otherwise None.

    """

    statement = select(Recipe).where(
        Recipe.id == recipe_id,
        Recipe.user_id == user_id,
    )

    result = db.execute(statement)

    return result.scalar_one_or_none()


def update_recipe_service(
    db: Session,
    user_id: int,
    recipe_id: int,
    data: RecipeCreate,
):
    recipe = get_user_recipe(
        db,
        user_id,
        recipe_id,
    )

    if recipe is None:
        return None

    recipe.title = data.title
    recipe.servings = data.servings
    recipe.is_user_modified = True

    recipe.ingredients.clear()

    for item in data.ingredients:
        ingredient = RecipeIngredient(
            quantity=item.quantity,
            unit=item.unit,
            ingredient=item.ingredient,
        )

        recipe.ingredients.append(ingredient)

    recipe.steps.clear()

    for item in data.steps:
        step = RecipeStep(
            step_number=item.step_number,
            instruction=item.instruction,
        )

        recipe.steps.append(step)

    try:
        db.commit()
        db.refresh(recipe)

    except Exception:
        db.rollback()
        raise

    return recipe
