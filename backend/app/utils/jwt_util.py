import jwt
from datetime import timedelta, datetime

from app.config.setting import settings


def create_access_token(data: dict, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()

    expires = datetime.now() + timedelta(minutes=expires_delta)

    to_encode["exp"] = expires

    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# def decode_access_token(token: str):
