FROM python:3.12-slim

WORKDIR /app

# Install uv
# RUN pip install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy only project metadata
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync

# Copy application
COPY . .

# Start FastAPI

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
