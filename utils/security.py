import os
import time
import binascii
import hashlib
import hmac
from typing import Dict
import jwt

from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

# Password hashing using PBKDF2-HMAC-SHA256
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    salt_hex = binascii.hexlify(salt).decode()
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return f"{salt_hex}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split('$')
    except Exception:
        return False
    salt = binascii.unhexlify(salt_hex)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100_000)
    return hmac.compare_digest(dk.hex(), hash_hex)


# JWT helpers
def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    now = int(time.time())
    expires = now + (expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    payload = {
        "sub": subject,
        "type": "access",
        "exp": expires,
        "iat": now,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(subject: str, expires_days: int | None = None) -> str:
    now = int(time.time())
    expires = now + (expires_days or REFRESH_TOKEN_EXPIRE_DAYS) * 24 * 3600
    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expires,
        "iat": now,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Dict:
    # Will raise jwt exceptions if invalid/expired
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
