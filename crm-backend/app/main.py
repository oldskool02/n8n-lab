from fastapi import FastAPI
import app.models
from app.routers import accounts, interaction, contacts, dashboard, auth

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mind Design CRM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later lock this down
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
app.include_router(interaction.router)
app.include_router(contacts.router)
app.include_router(dashboard.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"status": "CRM running"}