import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.exceptions import RecipeFatalError, RecipeGenericError
from app.routes.recipes import router as recipes_router
from app.routes.users import router as users_router


app = FastAPI()

logger = logging.getLogger(__name__)

app.include_router(recipes_router)
app.include_router(users_router)


@app.exception_handler(RecipeGenericError)
def recipe_generic_error_handler(
    request,
    exc: RecipeGenericError,
):
    logging.warning(
        "Recoverable recipe generation error: %s",
        exc,
    )

    return JSONResponse(
        status_code=503,
        content={
            "detail": "Please try again later"
        },
    )


@app.exception_handler(RecipeFatalError)
def recipe_fatal_error_handler(
    request,
    exc: RecipeFatalError,
):
    logger.exception(
        "Fatal recipe generation error: %s",
        exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred"
        },
    )


@app.get("/health")
def health():
    return {
        "status": "healthy"
        }


@app.get("/health/database")
def database_health(db: Session = Depends(get_db)):

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "healthy"
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
