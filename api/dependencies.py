from contextlib import contextmanager
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from api.db import get_connection, release_connection
from api.auth import decode_token

bearer_scheme = HTTPBearer()


# ── Database ─────────────────────────────────────────────────

def get_db() -> Generator:
    """
    Yields a psycopg2 connection from the pool.
    Commits on success, rolls back on any exception.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


# ── Authentication ────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Extract and validate the JWT from the Authorization header."""
    try:
        return decode_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


# ── Role guards ───────────────────────────────────────────────

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Admin access required.")
    return user


def require_lecturer(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Lecturer access required.")
    return user


def require_student(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Student access required.")
    return user
