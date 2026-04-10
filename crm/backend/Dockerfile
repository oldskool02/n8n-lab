FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

# CMD ["sh", "-c", "PYTHONPATH=/app python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8002"]
CMD ["sh", "-c", "PYTHONPATH=/app python -m app.create_db && alembic upgrade head && PYTHONPATH=/app python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8002"]