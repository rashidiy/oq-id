from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from settings.config import conf


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=conf.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, conf.SECRET_KEY, algorithm=conf.JWT_ALGORITHM)


def create_refresh_token(data: dict):
    expire = datetime.now() + timedelta(days=1)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, conf.SECRET_KEY, algorithm=conf.JWT_ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, conf.SECRET_KEY, algorithms=conf.JWT_ALGORITHM)
        return payload
    except JWTError:
        return None
