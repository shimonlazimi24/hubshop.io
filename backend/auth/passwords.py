import asyncio
import re
from concurrent.futures import ThreadPoolExecutor

import bcrypt
from fastapi import HTTPException, status

_executor = ThreadPoolExecutor(max_workers=4)

# Password policy constants
_MIN_LENGTH = 8
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$",
)
_PASSWORD_REQUIREMENTS = (
    "Password must be at least 8 characters and contain "
    "at least one uppercase letter, one lowercase letter, and one digit."
)


def validate_password(password: str) -> None:
    """Validate password meets security requirements.

    Raises HTTPException(400) if the password is too weak.
    """
    if len(password) < _MIN_LENGTH or not _PASSWORD_PATTERN.match(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_PASSWORD_REQUIREMENTS,
        )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


async def hash_password_async(password: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, hash_password, password)


async def verify_password_async(password: str, hashed: str) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, verify_password, password, hashed)
