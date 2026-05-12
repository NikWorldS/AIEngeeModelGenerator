import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, sessionmaker


load_dotenv()


def _get_database_url() -> str | URL:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB")

    if not user or not password or not db:
        raise RuntimeError(
            "Database connection is not configured. Set DATABASE_URL or "
            "POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB."
        )

    return URL.create(
        "postgresql+psycopg",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=db,
    )


engine: Engine = create_engine(_get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
