from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


class RecipeIngredientCreate(BaseModel):
    quantity: Decimal
    unit: str
    ingredient: str


class RecipeStepCreate(BaseModel):
    step_number: int
    instruction: str


class RecipeCreate(BaseModel):
    title: str
    servings: int

    ingredients: list[RecipeIngredientCreate]
    steps: list[RecipeStepCreate]


class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: Decimal
    unit: str
    ingredient: str


class RecipeStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    step_number: int
    instruction: str


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    servings: int
    is_user_modified: bool

    ingredients: list[RecipeIngredientResponse]
    steps: list[RecipeStepResponse]
