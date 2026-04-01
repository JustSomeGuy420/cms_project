import os
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
import bcrypt as _bcrypt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY    = os.getenv("JWT_SECRET", "change-this-secret")
ALGORITHM     = os.getenv("JWT_ALGORITHM", "HS256")
EXPIRE_HOURS  = int(os.getenv("JWT_EXPIRE_HOURS", "24"))


# ── Passwords ────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


# ── JWT ──────────────────────────────────────────────────────

def create_token(acc_id: int, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=EXPIRE_HOURS)
    payload = {"sub": str(acc_id), "role": role, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT.
    Raises JWTError if the token is invalid or expired.
    Returns {"acc_id": int, "role": str}.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    acc_id  = payload.get("sub")
    role    = payload.get("role")
    if acc_id is None or role is None:
        raise JWTError("Token payload missing required fields.")
    return {"acc_id": int(acc_id), "role": role}
