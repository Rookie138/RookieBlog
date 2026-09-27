import jwt
from datetime import timedelta, datetime, timezone

from app.config.setting import settings


def create_access_token(data: dict, expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()

    # 必须使用带时区的 UTC 时间：naive datetime 会被 PyJWT 当作服务器本地时间转成
    # 时间戳，一旦服务器时区（或容器 TZ）与开发机不一致，token 的过期时间就会整体偏移。
    now = datetime.now(timezone.utc)
    to_encode["exp"] = now + timedelta(minutes=expires_delta)
    to_encode["iat"] = now

    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

# def decode_access_token(token: str):
