"""Database initialization and session management."""

from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base
from .config import DEFAULT_DB_PATH

# Global engine and session factory
_engine = None
_SessionFactory = None


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize the database, creating tables if they don't exist."""
    global _engine, _SessionFactory

    if db_path is None:
        db_path = DEFAULT_DB_PATH

    db_url = f"sqlite:///{db_path}"
    _engine = create_engine(db_url, echo=False)
    _SessionFactory = sessionmaker(bind=_engine)

    # Create all tables
    Base.metadata.create_all(_engine)


def get_engine():
    """Get the database engine, initializing if needed."""
    global _engine
    if _engine is None:
        init_db()
    return _engine


def get_session() -> Session:
    """Get a new database session."""
    global _SessionFactory
    if _SessionFactory is None:
        init_db()
    return _SessionFactory()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_db_path(db_path: Path) -> None:
    """Set the database path and reinitialize."""
    global _engine, _SessionFactory
    _engine = None
    _SessionFactory = None
    init_db(db_path)
