from pydantic import BaseModel
from typing import Dict


class DocumentRequest(BaseModel):
    api_key: str
    template_name: str
    payload: Dict[str, str]


class DocumentResponse(BaseModel):
    document_id: str
    google_doc_id: str
    status: str