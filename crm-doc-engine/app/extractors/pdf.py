import fitz


def extract_pdf_text(file_bytes):
    
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    text = ""
    
    for page in doc:
        text += page.get_text()
    
    doc.close()
    
    return text