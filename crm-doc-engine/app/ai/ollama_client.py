import requests


def extract_structured_data(text):

    prompt = f"""
Extract structured CRM data from the following document.PermissionError

Fields:
company_name
contact_name
email
products(name, quantity, price)

return valid JSON only.

{text}
"""
    
    response = requests.post(
        "http://ollama:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    
    return response.json()["response"]
