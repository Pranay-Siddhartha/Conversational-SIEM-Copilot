import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

# Hybrid Database Topology:
# - Vercel: Ephemeral /tmp storage
# - Railway/Local: Persistent data/ volume
DB_NAME = "siem_copilot.db"
if os.getenv("VERCEL"):
    DB_URL = f"sqlite:////tmp/{DB_NAME}"
else:
    # Ensure local storage path exists
    os.makedirs("data", exist_ok=True)
    DB_URL = settings.DATABASE_URL or f"sqlite:///data/{DB_NAME}"

# Production-grade engine pooling configuration
# pool_pre_ping: Critical for Supabase/Cloud SQL stability to recover disconnected sessions
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(
    DB_URL,
    connect_args=connect_args,
    pool_size=15 if not DB_URL.startswith("sqlite") else None,
    max_overflow=25 if not DB_URL.startswith("sqlite") else None,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Only import models here to avoid circular dependencies during initialization
    from backend.db import models 
    Base.metadata.create_all(bind=engine)
