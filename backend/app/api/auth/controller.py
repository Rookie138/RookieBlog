from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
# from jwt import JWT
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.model import User
from app.config.setting import settings
from app.core.denpendencies import db_getter
from app.utils.hash_util import PwdHashUtil
from app.utils.jwt_util import create_access_token
from app.api.auth.schema import Token


router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: AsyncSession = Depends(db_getter)):

    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not PwdHashUtil.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    data = {
        'sub': user.id,
        'username': user.username
    }
    access_token = create_access_token(data=data)

    TokenSchema = Token(access_token=access_token, token_type="bearer")

    return TokenSchema



# @router.post("/login")
# async def login(
#     # form: OAuth2PasswordRequestForm = Depends(),
#     username: Annotated[str, Form()],
#     password: Annotated[str, Form()],
#     db: AsyncSession = Depends(db_getter),
# ):
#     stmt = select(User).where(User.username == username)
#     result = await db.execute(stmt)
#     user = result.scalar_one_or_none()
#
#     if not user or user.password != password:
#         raise HTTPException(status_code=401, detail="用户名或密码错误")
#
#
#     data = {
#         "sub": str(user.id),
#         "username": user.username,
#     }
#     token = create_access_token(data=data)
#     return {
#         "user_info":{
#             "id": user.id,
#             "username": user.username,
#             "name": user.name,
#         },
#         "token":{"access_token": token, "token_type": "bearer"}
#     }
