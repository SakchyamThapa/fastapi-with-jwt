import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Decide which DB URL to use
DATABASE_URL = (
    settings.DOCKER_URL
    if os.getenv("DOCKER") == "true"
    else settings.DATABASE_URL
)

print("RUNNING IN DOCKER:", os.getenv("DOCKER"))
print("USING DATABASE URL:", DATABASE_URL)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
