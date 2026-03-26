from pydantic_settings import BaseSettings


def get_secret(env_var, file_var):
    import os
    if file_var in os.environ:
        try:
            with open(os.environ[file_var], "r") as f:
                return f.read().strip()
        except Exception:
            pass
    return os.getenv(env_var)

class Settings(BaseSettings):
    db_host: str
    db_name: str
    db_user: str
    db_password: str = get_secret("DB_PASSWORD", "DB_PASSWORD_FILE")
    google_service_account_file: str

    class Config:
        env_file = ".env"


settings = Settings()