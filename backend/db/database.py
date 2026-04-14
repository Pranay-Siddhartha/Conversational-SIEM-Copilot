import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

# Standardized Vercel-safe path logic
DB_PATH = "/tmp/app.db" if os.getenv("VERCEL") else "data/app.db"

# Ensure the data directory exists locally
if not os.getenv("VERCEL") and not os.path.exists("data"):
    os.makedirs("data")

# Use environment override if provided, else default to Vercel-safe SQLite path
DATABASE_URL = settings.DATABASE_URL if settings.DATABASE_URL else f"sqlite:///{DB_PATH}"

# Handle SQLite specific connect args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
