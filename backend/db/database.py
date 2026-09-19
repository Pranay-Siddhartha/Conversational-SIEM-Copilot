import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

# Hybrid Database Topology:
# - Ephemeral: /tmp storage (Vercel, some serverless)
# - Render/Local: Use DATABASE_URL for persistent storage
DB_NAME = "siem_copilot.db"
if os.getenv("VERCEL"):
    DB_URL = f"sqlite:////tmp/{DB_NAME}"
else:
    # Ensure local storage path exists
    os.makedirs("data", exist_ok=True)
    DB_URL = settings.DATABASE_URL or f"sqlite:///data/{DB_NAME}"

# Production-grade engine pooling configuration
# pool_pre_ping: Critical for PostgreSQL stability to recover disconnected sessions
is_sqlite = DB_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine_kwargs = {
    "connect_args": connect_args,
    "pool_pre_ping": True,
}

# SQLite doesn't support pool_size/max_overflow — only set for PostgreSQL/MySQL
if not is_sqlite:
    engine_kwargs["pool_size"] = 15
    engine_kwargs["max_overflow"] = 25

engine = create_engine(DB_URL, **engine_kwargs)

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
