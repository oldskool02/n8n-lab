from fastapi import FastAPI, HTTPException
from app.database import get_connection

app = FastAPI()


@app.get("/health")
def health():
    return {
        "status": "healthy"
        }


@app.get("/health/database")
def database_health():
    try:
        conn = get_connection()

        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")

            conn.close()

        return {
            "status": "healthy",
            "database": "healthy"
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {e}"
        )
