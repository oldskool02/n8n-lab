from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID


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
    quantity: str
    unit: str
    ingredient: str


class RecipeStepCreate(BaseModel):
    step_number: int
    instruction: str


class RecipeUpdate(BaseModel):
    title: str
    servings: int

    ingredients: list[RecipeIngredientCreate]
    steps: list[RecipeStepCreate]


class RecipeIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: str
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


class RecipeGenerateRequest(BaseModel):
    request: str
    servings: int = Field(gt=0)
    dish: str | None = None
    diet: str | None = None
    cuisine: str | None = None


class GenerationCriteria(BaseModel):
    dish: str | None
    diet: str | None
    cuisine: str | None


class GeneratedRecipe(BaseModel):
    title: str
    servings: int
    ingredients: list[RecipeIngredientCreate]
    steps: list[RecipeStepCreate]


class GeneratedImage(BaseModel):
    generated: bool
    file_id: str | None


class RecipeGenerationResponse(BaseModel):
    request_id: UUID
    criteria: GenerationCriteria
    recipe: GeneratedRecipe
    image: GeneratedImage


class RecipeGenerationRequest(BaseModel):
    request_id: UUID
    request: str
    servings: int
    dish: str | None = None
    diet: str | None = None
    cuisine: str | None = None
    generate_image: bool


