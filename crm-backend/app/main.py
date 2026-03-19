from fastapi import FastAPI
import app.models
from app.routers import accounts, interaction, contacts

app = FastAPI(title="Mind Design CRM")

app.include_router(accounts.router)
app.include_router(interaction.router)
app.include_router(contacts.router)

@app.get("/")
def root():
    return {"status": "CRM running"}