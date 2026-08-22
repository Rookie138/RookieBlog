from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.model import User
from app.config.setting import settings
from app.core.denpendencies import db_getter

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterBody(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(body: RegisterBody, db: AsyncSession = Depends(db_getter)):
    username = body.username.strip()
    if not username or not body.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    exists = await db.execute(select(User).where(User.username == username))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(username=username, password=body.password)
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}


@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(db_getter),
):
    stmt = select(User).where(User.username == form.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or user.password != form.password:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {
            "sub": str(user.id),
            "name": user.username,
            "exp": expire,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}
