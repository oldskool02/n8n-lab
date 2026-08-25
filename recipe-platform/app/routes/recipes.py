from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import (
    RecipeUpdate,
    RecipeGenerateRequest,
    RecipeResponse)
from app.services.recipe_service import (
    delete_recipe_service,
    generate_recipe_service,
    get_user_recipes,
    get_user_recipe,
    update_recipe_service,
)


router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
)


@router.get("/", response_model=list[RecipeResponse])
def get_recipes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_recipes(db, current_user.id)


@router.post("/generate", response_model=RecipeResponse)
def generate_recipe(
    data: RecipeGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate_recipe_service(
        db,
        current_user.id,
        data,
    )


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = get_user_recipe(
        db,
        current_user.id,
        recipe_id,
    )

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return recipe


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = update_recipe_service(
        db,
        current_user.id,
        recipe_id,
        data,
    )

    if recipe is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return recipe


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_recipe_service(
        db,
        current_user.id,
        recipe_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe not found",
        )

    return None
