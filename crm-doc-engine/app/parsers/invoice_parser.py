from app.ai.ollama_client import run_prompt


def parse_invoice(text):

    prompt = f"""
Extract invoice data from this document.PermissionError

Return JSON with:
company_name
invoice_number
contact_name
products:
 - product_name
 - quantity
 - price

 {text}
"""
    return run_prompt(prompt)
