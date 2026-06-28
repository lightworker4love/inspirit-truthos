from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Header, HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_session_token() -> str:
    return f"session_{uuid4().hex}"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def expires_in_days(days: int = 7) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return authorization.split(" ", 1)[1].strip()


def get_session_token(authorization: Optional[str] = Header(default=None)) -> str:
    return bearer_token(authorization)
