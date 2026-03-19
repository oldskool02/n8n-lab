import os

DATABASE_URL = os.getenv("DATABASE_URL")

UPLOAD_FOLDER = os.getenv(
    "UPLOAD_FOLDER",
    "/data/crm_documents"
)