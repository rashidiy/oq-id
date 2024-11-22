from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from jose import JWTError, jwt

from settings.config import conf


class TokenManager:
    @staticmethod
    def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token with a 15-minute expiration by default."""
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, conf.SECRET_KEY, algorithm=conf.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        """Create a refresh token with a 15-day expiration."""
        expire = datetime.now(timezone.utc) + timedelta(days=15)
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, conf.SECRET_KEY, algorithm=conf.JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, conf.SECRET_KEY, algorithms=[conf.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
