import os
from pathlib import Path


def get_secret(secret_file: str | None) -> str | None:
    """
    Read the docker secret from a file.

    Returns None if no file was supplied
    """
    if not secret_file:
        return None

    return Path(secret_file).read_text().strip()

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")

DB_PASSWORD = get_secret(
    os.getenv("DB_PASSWORD_FILE")
)
