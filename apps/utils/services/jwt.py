from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt

from settings.config import conf


class TokenManager:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode.update({"exp": expire, "token_type": "access"})
        return jwt.encode(to_encode, conf.SECRET_KEY, algorithm=conf.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        expire = datetime.now(timezone.utc) + timedelta(days=15)
        to_encode = data.copy()
        to_encode.update({"exp": expire, "token_type": "refresh"})
        return jwt.encode(to_encode, conf.SECRET_KEY, algorithm=conf.JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
