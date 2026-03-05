from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_password: str
    google_service_account_file: str

    class Config:
        env_file = ".env"


settings = Settings()