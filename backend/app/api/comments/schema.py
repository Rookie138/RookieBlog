from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict



class CommentSchema(BaseModel):
    # id: int
    # article_id: int
    parent_id: int | None = None
    nickname: str
    email: EmailStr
    content: str

    model_config = ConfigDict(from_attributes=True)


class CommentOutSchema(BaseModel):
    id: int
    article_id: int
    parent_id: int | None = None
    nickname: str
    content: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)