from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
)
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import User
from app.schemas import (
    RecipeGenerateRequest,
    RecipeRegenerateRequest,
    RecipeResponse,
)
from app.services.recipe_service import (
    delete_recipe_service,
    generate_recipe_service,
    get_recipe_image_service,
    get_user_recipes,
    get_user_recipe,
    regenerate_recipe_service,
)
from app.services.pdf_service import create_recipe_pdf


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


@router.get("/{recipe_id}/image")
def get_recipe_image(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image_response = get_recipe_image_service(
        db,
        current_user.id,
        recipe_id,
    )

    if image_response is None:
        raise HTTPException(
            status_code=404,
            detail="Recipe image not found",
        )

    return Response(
        content=image_response.content,
        media_type=image_response.headers.get(
            "Content-Type",
            "image/png",
        ),
    )


@router.get("/{recipe_id}/pdf")
def get_recipe_pdf(
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

    image_response = get_recipe_image_service(
        db,
        current_user.id,
        recipe_id,
    )

    if image_response is not None:
        image_bytes = image_response.content
    else:
        image_bytes = None

    pdf_bytes = create_recipe_pdf(recipe, image_bytes)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
    )


@router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: int,
    data: RecipeRegenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    recipe = regenerate_recipe_service(
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
