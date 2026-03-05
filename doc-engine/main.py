from fastapi import FastAPI
from routers import document, health

app = FastAPI(
    title="Legal Document Engine",
    version="1.0.0"
)

app.include_router(document.router, prefix="/api/v1/documents")
app.include_router(health.router)