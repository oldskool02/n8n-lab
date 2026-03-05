from sqlalchemy.orm import Session
from models import SystemTemplate, Document
from services.google_service import get_google_services, copy_template, replace_placeholders
import uuid


class DocumentService:

    def __init__(self, db: Session):
        self.db = db
        self.docs_service, self.drive_service = get_google_services()

    def generate_document(self, firm, template_name, payload, request_ip):

        template = self.db.query(SystemTemplate).filter(
            SystemTemplate.template_name == template_name,
            SystemTemplate.active == True
        ).first()

        if not template:
            raise Exception("Template not found")

        new_doc_name = f"{template_name} - {uuid.uuid4()}"

        new_doc_id = copy_template(
            self.drive_service,
            template.google_doc_template_id,
            new_doc_name,
            firm.drive_generated_folder_id
        )

        replace_placeholders(self.docs_service, new_doc_id, payload)

        document = Document(
            firm_id=firm.id,
            template_id=template.id,
            google_doc_id=new_doc_id,
            document_name=new_doc_name,
            status="generated",
            request_ip=request_ip
        )

        self.db.add(document)
        self.db.commit()

        return {
            "document_id": str(document.id),
            "google_doc_id": new_doc_id,
            "status": "generated"
        }