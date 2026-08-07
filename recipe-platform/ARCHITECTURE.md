# Why FastAPI talks to n8n

FastAPI owns the business logic.

n8n owns workflow orchestration.

Therefore FastAPI calls n8n.

# Why only FastAPI writes to PostgreSQL

PostgreSQL is the single source of truth.

FastAPI owns recipe management.

n8n never writes directly to the database.

Laptop Browser
        │
        ▼
192.168.101.110:8001
        │
Docker Port Mapping
        │
recipe-platform Container
        │
uv
        │
Uvicorn
        │
FastAPI
        │
/health