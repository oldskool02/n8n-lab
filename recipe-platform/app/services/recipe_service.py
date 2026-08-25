import httpx

from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Recipe, RecipeIngredient, RecipeStep
from app.schemas import (
    RecipeUpdate,
    RecipeGenerateRequest,
    RecipeGenerationRequest,
    RecipeGenerationResponse,
)
from app.config import N8N_INTERNAL_KEY
from app.exceptions import RecipeFatalError, RecipeGenericError


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


def generate_recipe_service(
    db: Session,
    user_id: int,
    data: RecipeGenerateRequest,
):
    request_id = uuid4()

    generation_request = RecipeGenerationRequest(
        request_id=request_id,
        request=data.request,
        servings=data.servings,
        dish=data.dish,
        diet=data.diet,
        cuisine=data.cuisine,
        generate_image=False,
    )

    try:
        response = httpx.post(
            "http://n8n:5678/webhook/recipe-generation",
            headers={
                "X-Recipe-Platform-Key": N8N_INTERNAL_KEY,
            },
            json=generation_request.model_dump(mode="json"),
            timeout=10,
        )

    except httpx.RequestError as exc:
        raise RecipeGenericError(
            "Could not communicate with n8n",
        ) from exc

    if not 200 <= response.status_code < 300:
        raise RecipeFatalError(
            f"n8n returned HTTP {response.status_code}"
        )

    try:
        response_data = response.json()

    except ValueError as exc:
        raise RecipeFatalError(
            "n8n returned invalid JSON"
        ) from exc

    try:
        generation_response = RecipeGenerationResponse.model_validate(
            response_data,
        )

    except ValidationError as exc:
        raise RecipeFatalError(
            "n8n returned an invalid recipe generation response"
        ) from exc

    if generation_response.request_id != request_id:
        raise RecipeFatalError(
            "n8n returned a different request_id"
        )

    if generation_response.recipe.servings != data.servings:
        raise RecipeFatalError(
            "n8n returned different servings than requested"
        )

    recipe = _create_generated_recipe(
        db=db,
        user_id=user_id,
        generation_response=generation_response,
    )

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
    data: RecipeUpdate,
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


def delete_recipe_service(
    db: Session,
    user_id: int,
    recipe_id: int,
):
    recipe = get_user_recipe(
        db,
        user_id,
        recipe_id,
    )

    if recipe is None:
        return None

    try:
        db.delete(recipe)
        db.commit()

    except Exception:
        db.rollback()
        raise

    return True


def _create_generated_recipe(
    db: Session,
    user_id: int,
    generation_response: RecipeGenerationResponse,
):
    recipe = Recipe(
        user_id=user_id,
        generation_request_id=generation_response.request_id,
        title=generation_response.recipe.title,
        servings=generation_response.recipe.servings,
    )

    for item in generation_response.recipe.ingredients:
        ingredient = RecipeIngredient(
            quantity=item.quantity,
            unit=item.unit,
            ingredient=item.ingredient,
        )

        recipe.ingredients.append(ingredient)

    for item in generation_response.recipe.steps:
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
