from sqlalchemy import create_engine, text

# connect to default postgres DB (NOT crm)
DB_URL = "postgresql://n8n:Marie1964@postgres:5432/postgres"

engine = create_engine(DB_URL)

def create_database():
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        try:
            conn.execute(text("CREATE DATABASE crm"))
            print("Database 'crm' created")
        except Exception:
            print("Database 'crm' already exists")

if __name__ == "__main__":
    create_database()
