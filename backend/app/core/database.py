from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=10)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db


def init_db() -> None:
    """Create ORM tables (public schema) and seed the `lab` sandbox schema once."""
    from app import models  # noqa: F401  (register models)

    seed = (Path(__file__).resolve().parents[1] / "lab_seed.sql").read_text()
    with engine.begin() as conn:
        conn.execute(text("SELECT pg_advisory_xact_lock(42)"))  # api + worker race-safe
        Base.metadata.create_all(conn)
        if not conn.execute(text("SELECT to_regclass('lab.employees')")).scalar():
            conn.connection.cursor().execute(seed)
