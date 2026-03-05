from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

DATABASE_URL = (
    f"postgresql+psycopg2://{settings.db_user}:"
    f"{settings.db_password}@{settings.db_host}/"
    f"{settings.db_name}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()