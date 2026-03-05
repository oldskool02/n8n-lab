# schemas.py

from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime


class RecipeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    ingredients: List[str]
    instructions: List[str]

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v

    @field_validator("ingredients", "instructions")
    @classmethod
    def validate_lists(cls, values: List[str]):
        if not values:
            raise ValueError("List cannot be empty")

        cleaned = []
        for item in values:
            item = item.strip()
            if not item:
                raise ValueError("List items cannot be empty")
            cleaned.append(item)

        return cleaned


class RecipeOut(BaseModel):
    id: int
    title: str
    ingredients: List[str]
    instructions: List[str]
    created_at: datetime


class RecipeUpdate(BaseModel):
    title: str | None = None
    ingredients: List[str] | None = None
    instructions: List[str] | None = None

class RecipeGenerate(BaseModel):
    prompt: str