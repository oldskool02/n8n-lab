def classify_document(text):
    
    if "invoice" in text.lower():
        return "Invoice"
    
    if "quotation" in text.lower():
        return "quote"
    
    if "quote" in text.lower():
        return "quote"
    
    if "purchase order" in text.lower():
        return "purchase_order"
    
    return "Unknown"
