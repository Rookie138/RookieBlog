from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ArticleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    summary: Optional[str] = None
    status: Optional[str] = None


class ArticleDetail(ArticleSummary):
    context: str
    created_at: Optional[datetime] = None


class ArticleCreate(BaseModel):
    slug: str
    title: str
    summary: Optional[str] = ""
    status: str = "draft"
    context: str = ""


class ArticleUpdate(BaseModel):
    slug: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    context: Optional[str] = None
