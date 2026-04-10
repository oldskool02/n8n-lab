import os

def get_secret(env_var, file_var):
    if file_var in os.environ:
        try:
            with open(os.environ[file_var], "r") as f:
                return f.read().strip()
        except Exception:
            pass
    return os.getenv(env_var)


# Try new pattern first (secrets-based)
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = get_secret("DB_PASSWORD", "DB_PASSWORD_FILE")

if DB_HOST and DB_NAME and DB_USER and DB_PASSWORD:
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"
else:
    # Fallback to old behavior (safe)
    DATABASE_URL = os.getenv("DATABASE_URL")


UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "/data/crm_documents"
)