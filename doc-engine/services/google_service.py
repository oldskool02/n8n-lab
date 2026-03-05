from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import settings


SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]


def get_google_services():
    credentials = service_account.Credentials.from_service_account_file(
        settings.google_service_account_file,
        scopes=SCOPES
    )

    docs_service = build("docs", "v1", credentials=credentials)
    drive_service = build("drive", "v3", credentials=credentials)

    return docs_service, drive_service


def copy_template(drive_service, template_id, new_name, folder_id):
    copied_file = drive_service.files().copy(
        fileId=template_id,
        body={
            "name": new_name,
            "parents": [folder_id]
        }
    ).execute()

    return copied_file["id"]


def replace_placeholders(docs_service, document_id, payload: dict):
    requests = []

    for key, value in payload.items():
        requests.append({
            "replaceAllText": {
                "containsText": {
                    "text": f"{{{{{key}}}}}",
                    "matchCase": True
                },
                "replaceText": str(value) if value else ""
            }
        })

    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": requests}
    ).execute()