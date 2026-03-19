from app.ai.ollama_client import run_prompt

def parse_quote(text):

    prompt = f"""
Extract quotation data from this document.

Return JSON with:

company_name
quote_number
contact_name
products:
  - product_name
  - quantity
  - price

{text}
"""

    return run_prompt(prompt)