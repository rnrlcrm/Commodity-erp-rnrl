from __future__ import annotations

from passlib.context import CryptContext

from backend.core.settings.config import settings


def _context() -> CryptContext:
    scheme = settings.PASSWORD_SCHEME.lower()
    if scheme == "bcrypt":
        return CryptContext(schemes=["bcrypt"], deprecated="auto")
    return CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class PasswordHasher:
    def __init__(self) -> None:
        self._ctx = _context()

    def hash(self, password: str) -> str:
        return self._ctx.hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return self._ctx.verify(password, hashed)
