from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from jose import JWTError, jwt

from settings.config import conf


class TokenManager:
    @staticmethod
    def _create_token(data: Dict, expires_in: timedelta, token_type: str) -> str:
        """
        :param data: Payload data for the token.
        :param expires_in: Expiration time as timedelta.
        :param token_type: Token type (e.g., "access" or "refresh").
        :return: Encoded JWT string.
        """
        expire = datetime.now(timezone.utc) + expires_in
        payload = {
            **data,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": token_type,
        }
        return jwt.encode(payload, conf.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def create_access_token(data: Dict) -> str:
        expires_in = timedelta(minutes=int(conf.ACCESS_TOKEN_EXPIRE_MINUTES))
        return TokenManager._create_token(data, expires_in, "access")

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        expires_in = timedelta(days=int(conf.REFRESH_TOKEN_EXPIRE_DAYS))
        return TokenManager._create_token(data, expires_in, "refresh")

    @staticmethod
    def verify_token(token: str, expected_type: Optional[str] = None) -> Optional[Dict]:
        """
        Decode and verify a JWT token, optionally checking its type.
        :param token: The JWT token string to decode.
        :param expected_type: Optional expected type of the token ('access' or 'refresh').
        :return: Decoded payload if valid, else None.
        """
        try:
            payload = jwt.decode(token, conf.SECRET_KEY, algorithms=["HS256"])
            if expected_type and payload.get("type") != expected_type:
                return None
            return payload
        except JWTError:
            return None
