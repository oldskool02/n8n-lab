from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from app.database import SessionLocal

app = FastAPI()


@app.get("/health")
def health():
    return {
        "status": "healthy"
        }


@app.get("/health/database")
def database_health():
    session = SessionLocal()

    try:
        session.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "healthy"
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {e}"
        )
    finally:
        session.close()
