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
# Handle SQLite specific connect args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Production-grade engine pooling:
# - pool_pre_ping: Verifies connection health before use, essential for Supabase/Cloud envs
# - pool_size: Base connection pool (SaaS-ready)
# - max_overflow: Allow burst connections
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=10 if not DATABASE_URL.startswith("sqlite") else None,
    max_overflow=20 if not DATABASE_URL.startswith("sqlite") else None,
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
    Base.metadata.create_all(bind=engine)
