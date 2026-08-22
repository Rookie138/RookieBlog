from enum import Enum

from app.core.base_model import Base, TimeMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ForeignKey


class ArticleStatus(str, Enum):
    published = "published"
    draft = "draft"
    deleted = "deleted"


class Article(Base, TimeMixin):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    slug: Mapped[str] = mapped_column(String(50), comment="SEO友好链接")
    title: Mapped[str] = mapped_column(String(50), nullable=False, comment="标题")
    summary: Mapped[str] = mapped_column(String(255), nullable=True, comment="简介")
    context: Mapped[str] = mapped_column(Text, comment="文章内容")
    status: Mapped[str] = mapped_column(String(25), default="draft", comment="文章状态")
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), comment="作者ID")
