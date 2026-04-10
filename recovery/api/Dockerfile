FROM python:3.11-slim

WORKDIR /app

COPY recovery/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY recovery/api/main.py .
COPY scripts /app/scripts
COPY recovery/ui /app/ui

RUN chmod +x /app/scripts/*.sh

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050"]
