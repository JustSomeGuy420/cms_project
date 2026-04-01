import os
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

_pool: pool.ThreadedConnectionPool = None


def init_pool() -> None:
    global _pool
    dsn = (
        f"host={os.getenv('DB_HOST', 'localhost')} "
        f"port={os.getenv('DB_PORT', '5432')} "
        f"dbname={os.getenv('DB_NAME', 'cms_db')} "
        f"user={os.getenv('DB_USER', 'cms_user')} "
        f"password={os.getenv('DB_PASSWORD', 'cms_password')}"
    )
    _pool = pool.ThreadedConnectionPool(minconn=2, maxconn=20, dsn=dsn)


def get_connection() -> psycopg2.extensions.connection:
    if _pool is None:
        raise RuntimeError("Connection pool not initialised. Call init_pool() first.")
    return _pool.getconn()


def release_connection(conn: psycopg2.extensions.connection) -> None:
    _pool.putconn(conn)


def get_cursor(conn):
    """Return a RealDictCursor so rows come back as dicts."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
