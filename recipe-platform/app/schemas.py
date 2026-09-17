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
    cuisine: str | None
    image_file_id: str | None
    is_user_modified: bool

    ingredients: list[RecipeIngredientResponse]
    steps: list[RecipeStepResponse]


class RecipeGenerateRequest(BaseModel):
    request: str = Field(min_length=6)
    servings: int = Field(gt=0)
    diet: str | None = None
    cuisine: str | None = None

    @field_validator("request", mode="before")
    @classmethod
    def validate_request(cls, value: str) -> str:
        value = value.strip()

        if len(value) < 6:
            raise ValueError(
                "Request must be at least 6 characters long"
            )

        return value


class RecipeRegenerateRequest(BaseModel):
    servings: int = Field(gt=0)
    diet: str | None = None
    cuisine: str | None = None


class GenerationCriteria(BaseModel):
    diet: str | None
    cuisine: str | None


class GeneratedRecipe(BaseModel):
    title: str
    servings: int
    ingredients: list[RecipeIngredientCreate]
    steps: list[RecipeStepCreate]


class RecipeRegenerationRequest(BaseModel):
    request_id: UUID
    title: str
    current_recipe: GeneratedRecipe
    servings: int
    diet: str | None = None
    cuisine: str | None = None


class RecipeRegenerationResponse(BaseModel):
    request_id: UUID
    recipe: GeneratedRecipe


class GeneratedImage(BaseModel):
    generated: bool
    file_id: str | None


class RecipeGenerationResponse(BaseModel):
    request_id: UUID
    criteria: GenerationCriteria
    is_recipe_request: bool
    recipe: GeneratedRecipe
    image: GeneratedImage


class RecipeGenerationRequest(BaseModel):
    request_id: UUID
    request: str
    servings: int
    diet: str | None = None
    cuisine: str | None = None
    generate_image: bool
