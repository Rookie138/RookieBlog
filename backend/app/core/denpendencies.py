from typing import AsyncGenerator, Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.model import User
from app.config.setting import settings
from app.core.database import async_session_local

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def db_getter() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        async with session.begin():
            yield session


async def redis_getter():
    pass


async def get_current_user(
    token:  Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(db_getter),
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="登录已过期或无效")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
