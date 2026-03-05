# main.py

from fastapi import FastAPI, HTTPException, Query
from typing import List
import logging
import httpx
from schemas import RecipeGenerate

from schemas import RecipeCreate, RecipeOut, RecipeUpdate
import db


app = FastAPI()

# Structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recipes", response_model=RecipeOut)
def create_recipe(recipe: RecipeCreate):
    logging.info("Creating recipe")
    result = db.create_recipe(recipe)
    return result


@app.get("/recipes", response_model=List[RecipeOut])
def list_recipes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return db.get_recipes(limit, offset)


@app.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int):
    recipe = db.get_recipe_by_id(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return recipe


@app.put("/recipes/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, recipe: RecipeUpdate):
    updated = db.update_recipe(recipe_id, recipe)

    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")

    logging.info(f"Updated recipe {recipe_id}")
    return updated


@app.delete("/recipes/{recipe_id}")
def delete_recipe(recipe_id: int):
    success = db.delete_recipe(recipe_id)

    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")

    logging.info(f"Deleted recipe {recipe_id}")
    return {"deleted": True}

@app.post("/recipes/generate", response_model=RecipeOut)
async def generate_recipe(data: RecipeGenerate):

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://n8n:5678/webhook/agent",
            json={"message": data.prompt}
        )

    if response.status_code != 200:
        raise HTTPException(
        status_code=500,
        detail=f"n8n failed: {response.status_code} - {response.text}"
    )
    

    recipe_json = response.json()

    recipe = RecipeCreate(
        title=recipe_json["title"],
        ingredients=recipe_json["ingredients"],
        instructions=recipe_json["instructions"]
    )

    result = db.create_recipe(recipe)

    return result
