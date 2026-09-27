from typing import Annotated


from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.model import User
from app.core.denpendencies import db_getter, limiter_request
from app.utils.hash_util import PwdHashUtil
from app.utils.jwt_util import create_access_token
from app.api.auth.schema import Token

# from app.common.response import SuccessResponse


router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(limiter_request)])



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
        'sub': str(user.id),
        'username': user.username
    }
    access_token = create_access_token(data=data)

    TokenSchema = Token(access_token=access_token, token_type="bearer")

    return TokenSchema



