import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from .env file
load_dotenv()

def get_database_url() -> str:
    """Reads and normalizes DATABASE_URL from .env with explicit psycopg2 driver."""
    load_dotenv(override=True)
    raw_db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/placement_db"
    )
    if raw_db_url.startswith("postgresql://"):
        return raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return raw_db_url


# SQLAlchemy declarative base for ORM models
Base = declarative_base()

# Lazy engine initialization
_engine = None
_SessionLocal = None
_current_db_url = None


def get_engine():
    """Returns an engine bound to the current DATABASE_URL in .env."""
    global _engine, _current_db_url
    target_url = get_database_url()

    if _engine is None or _current_db_url != target_url:
        _engine = create_engine(
            target_url,
            pool_pre_ping=True,
            echo=False
        )
        _current_db_url = target_url
    return _engine


def get_session_factory():
    """Returns a singleton sessionmaker bound to the engine."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal


def get_db():
    """
    Context generator yielding a SQLAlchemy session.
    Closes the session cleanly upon exit.
    """
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """
    Tests database connection and checks if the 'vector' extension is available.
    Returns:
        dict: {
            "connected": bool,
            "version": str or None,
            "pgvector_enabled": bool,
            "message": str
        }
    """
    result = {
        "connected": False,
        "version": None,
        "pgvector_enabled": False,
        "message": ""
    }

    try:
        engine = get_engine()
        with engine.connect() as conn:
            # 1. Test basic connectivity & fetch Postgres version
            version_row = conn.execute(text("SELECT version();")).fetchone()
            result["connected"] = True
            result["version"] = version_row[0] if version_row else "Unknown"

            # 2. Check if pgvector extension is installed
            ext_check = conn.execute(
                text("SELECT extname FROM pg_extension WHERE extname = 'vector';")
            ).fetchone()

            if ext_check:
                result["pgvector_enabled"] = True
                result["message"] = "Connected successfully. pgvector extension is active."
            else:
                result["pgvector_enabled"] = False
                result["message"] = (
                    "Connected to PostgreSQL, but 'vector' extension is not enabled yet. "
                    "Run 'CREATE EXTENSION IF NOT EXISTS vector;' in the database."
                )

    except Exception as e:
        result["connected"] = False
        result["message"] = f"Database connection failed: {str(e)}"

    return result
