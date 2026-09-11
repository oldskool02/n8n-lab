import httpx

from uuid import uuid4

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Recipe,
    RecipeIngredient,
    RecipeStep
)

from app.schemas import (
    GeneratedImage,
    RecipeUpdate,
    RecipeGenerateRequest,
    RecipeGenerationRequest,
    RecipeGenerationResponse,
    RecipeRegenerateRequest,
    RecipeRegenerationRequest,
    RecipeRegenerationResponse,
)
from app.config import N8N_INTERNAL_KEY
from app.exceptions import (
    RecipeFatalError,
    RecipeGenericError,
    RecipeInvalidRequestError,
)


def regenerate_recipe_service(
    db: Session,
    user_id: int,
    recipe_id: int,
    data: RecipeRegenerateRequest,
):
    recipe = get_user_recipe(
        db,
        user_id,
        recipe_id,
    )

    if recipe is None:
        return None

    regeneration_request_id = uuid4()

    regeneration_request = RecipeRegenerationRequest(
        request_id=regeneration_request_id,
        title=recipe.title,
        current_recipe={
            "title": recipe.title,
            "servings": recipe.servings,
            "ingredients": [
                {
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "ingredient": item.ingredient,
                }
                for item in recipe.ingredients
            ],
            "steps": [
                {
                    "step_number": item.step_number,
                    "instruction": item.instruction,
                }
                for item in recipe.steps
            ],
        },
        servings=data.servings,
        dish=data.dish,
        diet=data.diet,
        cuisine=data.cuisine,
    )

    try:
        response_data = httpx.post(
            "http://n8n:5678/webhook/recipe-regeneration",
            headers={
                "X-Recipe-Platform-Key": N8N_INTERNAL_KEY,
            },
            json=regeneration_request.model_dump(mode="json"),
            timeout=60,
        )
    except httpx.RequestError as exc:
        raise RecipeGenericError(
            "Could not communicate with n8n",
        ) from exc

    if not 200 <= response_data.status_code < 300:
        raise RecipeFatalError(
            f"n8n returned HTTP {response_data.status_code}"
        )

    try:
        response_data = response_data.json()

    except ValueError as exc:
        raise RecipeFatalError(
            "n8n returned invalid JSON"
        ) from exc

    try:
        regeneration_response = RecipeRegenerationResponse.model_validate(
            response_data,
        )

    except ValidationError as exc:
        raise RecipeFatalError(
            "n8n returned an invalid recipe regeneration response"
        ) from exc

    if regeneration_response.request_id != regeneration_request_id:
        raise RecipeFatalError(
            "n8n returned a different request_id"
        )

    if regeneration_response.recipe.servings != data.servings:
        raise RecipeFatalError(
            "n8n returned different servings than requested"
        )

    recipe.servings = regeneration_response.recipe.servings
    recipe.is_user_modified = True
    recipe.dish = data.dish
    recipe.diet = data.diet
    recipe.cuisine = data.cuisine

    recipe.ingredients.clear()

    for item in regeneration_response.recipe.ingredients:
        ingredient = RecipeIngredient(
            quantity=item.quantity,
            unit=item.unit,
            ingredient=item.ingredient,
        )

        recipe.ingredients.append(ingredient)

    recipe.steps.clear()

    for item in regeneration_response.recipe.steps:
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
            timeout=60,
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

    if not generation_response.is_recipe_request:
        raise RecipeInvalidRequestError(
            "This is a Recipe Generator. Please specify a meal/main ingredient you want the recipe for."
        )

    recipe = _create_generated_recipe(
        db=db,
        user_id=user_id,
        generation_response=generation_response,
    )

    try:
        image_response = httpx.post(
            "http://n8n:5678/webhook/recipe-image-generation",
            headers={
                "X-Recipe-Platform-Key": N8N_INTERNAL_KEY,
            },
            json={
                "title": recipe.title,
                "dish": recipe.dish,
                "diet": recipe.diet,
                "cuisine": recipe.cuisine,
            },
            timeout=60,
        )

    except httpx.RequestError:
        return recipe

    if 200 <= image_response.status_code < 300:
        try:
            image_result = GeneratedImage.model_validate(
                image_response.json(),
            )

        except (ValidationError, ValueError):
            return recipe

        if image_result.generated and image_result.file_id:
            recipe.image_file_id = image_result.file_id

            try:
                db.commit()
                db.refresh(recipe)

            except Exception:
                db.rollback()

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

    recipe_id_value = recipe.id
    recipe_title = recipe.title
    image_file_id = recipe.image_file_id

    try:
        db.delete(recipe)
        db.commit()

    except Exception:
        db.rollback()
        raise

    if image_file_id:
        try:
            httpx.post(
                "http://n8n:5678/webhook/recipe-image-deletion",
                headers={
                    "X-Recipe-Platform-Key": N8N_INTERNAL_KEY,
                },
                json={
                    "recipe_id": recipe_id_value,
                    "recipe_title": recipe_title,
                    "file_id": image_file_id,
                },
                timeout=60,
            )
        except httpx.RequestError:
            pass

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
        dish = generation_response.criteria.dish,
        diet = generation_response.criteria.diet,
        cuisine = generation_response.criteria.cuisine,
        image_file_id = generation_response.image.file_id,
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


def get_recipe_image_service(
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

    if not recipe.image_file_id:
        return None

    try:
        response = httpx.post(
            "http://n8n:5678/webhook/recipe-image-retrieval",
            headers={
                "X-Recipe-Platform-Key": N8N_INTERNAL_KEY,
            },
            json={
                "file_id": recipe.image_file_id,
            },
            timeout=60,
        )

    except httpx.RequestError as exc:
        return None

    if not 200 <= response.status_code < 300:
        return None

    return response
