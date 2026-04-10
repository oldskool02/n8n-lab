from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from schemas import DocumentRequest, DocumentResponse
from dependencies import get_db
from services.auth_service import validate_api_key
from services.document_service import DocumentService

router = APIRouter()


@router.post("/generate", response_model=DocumentResponse)
def generate_document(
    request_data: DocumentRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    firm = validate_api_key(db, request_data.api_key)

    service = DocumentService(db)

    result = service.generate_document(
        firm,
        request_data.template_name,
        request_data.payload,
        request.client.host
    )

    return result