from pydantic import BaseModel, ConfigDict, Field, field_validator
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
    diet: str | None
    image_file_id: str | None
    is_user_modified: bool

    ingredients: list[RecipeIngredientResponse]
    steps: list[RecipeStepResponse]


class RecipeGenerateRequest(BaseModel):
    request: str = Field(min_length=1)

    @field_validator("request", mode="before")
    @classmethod
    def validate_request(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Please enter a recipe request"
            )

        return value


class GeneratedRecipe(BaseModel):
    title: str
    servings: int
    diet: str | None = None
    ingredients: list[RecipeIngredientCreate]
    steps: list[RecipeStepCreate]


class GeneratedImage(BaseModel):
    generated: bool
    file_id: str | None


class RecipeGenerationResponse(BaseModel):
    request_id: UUID
    is_recipe_request: bool
    needs_clarification: bool
    clarification_message: str | None = None
    recipe: GeneratedRecipe | None = None
    image: GeneratedImage


class RecipeRefineRequest(BaseModel):
    request: str = Field(min_length=1)


class RecipeRefinePayload(BaseModel):
    request: str
    current_recipe: GeneratedRecipe


class RecipeRefineResponse(BaseModel):
    recipe: GeneratedRecipe


class RecipeGenerationRequest(BaseModel):
    request_id: UUID
    request: str
