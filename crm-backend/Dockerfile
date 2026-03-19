FROM python:3.11

WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app ./app

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]