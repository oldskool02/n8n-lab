from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routes.recipes import router as recipes_router
from app.routes.users import router as users_router

app = FastAPI()

app.include_router(recipes_router)
app.include_router(users_router)


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
