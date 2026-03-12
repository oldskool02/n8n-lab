# main.py

from urllib import response
from fastapi import FastAPI, HTTPException, Query
from typing import List
import logging
import httpx
import asyncio
from schemas import RecipeGenerate
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse

from schemas import RecipeCreate, RecipeOut, RecipeUpdate
import db


app = FastAPI()

app.mount("/app", StaticFiles(directory="frontend", html=True), name="frontend")

conversation_memory = []

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
    logging.info(f"Creating recipe for user {recipe.user_id}")
    result = db.create_recipe(recipe)
    return result


@app.get("/recipes", response_model=List[RecipeOut])
def list_recipes(
    user_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    return db.get_recipes(limit, offset)


@app.get("/recipes/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, user_id: str = Query(...)):
    recipe = db.get_recipe_by_id(recipe_id, user_id)

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
async def delete_recipe(recipe_id: int):

    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM recipes WHERE id = %s RETURNING id",
        (recipe_id,)
    )

    deleted = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"deleted": recipe_id}

@app.post("/recipes/generate", response_model=RecipeOut)
async def generate_recipe(data: RecipeGenerate):

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "http://n8n:5678/webhook/agent",
            json={"message": data.prompt,
                  "user_id": data.user_id
                  }
        )

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="AI generation failed")

    recipe_json = response.json()

    # Validate AI output
    recipe = RecipeCreate(
        user_id=data.user_id,
        **recipe_json
    )

    # Save to database
    result = db.create_recipe(recipe)

    return result


@app.get("/")
def root():
    return {"service": "recipe-api", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/recipes/stream")
async def generate_recipe_stream(data: RecipeGenerate):

    async def event_stream():

        async with httpx.AsyncClient(timeout=None) as client:

            conversation_memory.append({
                "role": "user",
                "content": data.prompt
            })

            response = await client.post(
                "http://n8n:5678/webhook/agent",
                json={
                    "message": data.prompt,
                    "history": conversation_memory
                }
            )

            recipe = response.json()

            # Handle recipe list (e.g. "show my recipes")
            if isinstance(recipe, list):
                for r in recipe:
                    yield f"TITLE:{r.get('title','Unknown')}\n"
                    await asyncio.sleep(0.3)
                return

            # Only save if this looks like a real recipe
            if "ingredients" in recipe and "instructions" in recipe:
                saved = create_recipe(RecipeCreate(**recipe))

            if "title" in recipe:
                conversation_memory.append({
                    "role": "assistant",
                    "content": recipe["title"]
                })

            # conversation_memory.append({
            #     "role": "assistant",
            #     "content": recipe["title"]
            # })            
            
            # recipe = response.json()

            # # Handle recipe list (e.g. "show my recipes")
            # if isinstance(recipe, list):
            #     for r in recipe:
            #         yield f"TITLE:{r['title']}\n"
            #         await asyncio.sleep(0.3)
            #     return
            
            # # Save the recipe here
            # saved = create_recipe(RecipeCreate(**recipe))

            # conversation_memory.append({
            #     "role": "assistant",
            #     "content": recipe["title"]
            # })

            # Save the recipe
            # saved = create_recipe(RecipeCreate(**recipe))

            if len(conversation_memory) > 10:
                conversation_memory.pop(0)

            # Stream title
            yield f"TITLE:{recipe['title']}\n"
            await asyncio.sleep(0.4)

            for ing in recipe["ingredients"]:
                yield f"ING:{ing}\n"
                await asyncio.sleep(0.25)

            for step in recipe["instructions"]:
                yield f"STEP:{step}\n"
                await asyncio.sleep(0.35)

    return StreamingResponse(event_stream(), media_type="text/plain")
