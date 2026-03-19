from fastapi import APIRouter, UploadFile
import shutil
import os

from ..config import UPLOAD_FOLDER

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload")
def upload_document(file: UploadFile):

    path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"uploaded": file.filename}