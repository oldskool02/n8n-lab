from fastapi import FastAPI, UploadFile, File

from app.extractors.pdf import extract_pdf_text
from app.classifiers.document_classifier import classify_document
from app.parsers.invoice_parser import parse_invoice
from app.parsers.quote_parser import parse_quote

app = FastAPI(title="CRM Document Engine")


@app.post("/extract/")
async def extract(file: UploadFile = File(...)):

    file_bytes = await file.read()

    text = extract_pdf_text(file_bytes)

    doc_type = classify_document(text)

    if doc_type == "Invoice":
        result = parse_invoice(text)

    elif doc_type == "quote":
        result = parse_quote(text)

    else:
        result = {"error": "Unknown document type"}

    return {
        "document_type": doc_type, 
        "data": result}
