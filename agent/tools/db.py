"""Utilitaires de connexion SQLAlchemy pour MySQL et PostgreSQL."""

import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

DEFAULT_MYSQL_URL = (
    "mysql+pymysql://root:@localhost:3306/copilote_db?charset=utf8mb4"
)
DEFAULT_POSTGRES_URL = "postgresql://user:password@localhost:5433/pme_db"

INVALID_MYSQL_PARAMS = {
    "createDatabaseIfNotExist",
    "useSSL",
    "serverTimezone",
}


def _sanitize_mysql_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme.startswith("mysql") and parsed.query:
        query = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k not in INVALID_MYSQL_PARAMS
        ]
        return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
    return url


def get_mysql_database_url() -> str:
    return os.getenv("MYSQL_DATABASE_URL", DEFAULT_MYSQL_URL)


def get_postgres_database_url() -> str:
    return os.getenv("POSTGRES_DATABASE_URL", DEFAULT_POSTGRES_URL)


def get_mysql_sqlalchemy_url() -> str:
    return _sanitize_mysql_url(get_mysql_database_url())


def get_postgres_sqlalchemy_url() -> str:
    url = get_postgres_database_url()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


_mysql_engine: Engine | None = None
_postgres_engine: Engine | None = None


def get_mysql_engine() -> Engine:
    global _mysql_engine
    if _mysql_engine is None:
        _mysql_engine = create_engine(get_mysql_sqlalchemy_url())
    return _mysql_engine


def get_postgres_engine() -> Engine:
    global _postgres_engine
    if _postgres_engine is None:
        _postgres_engine = create_engine(get_postgres_sqlalchemy_url())
    return _postgres_engine


def get_engine() -> Engine:
    """Alias historique pour l'engine MySQL du sales_agent."""
    return get_mysql_engine()
