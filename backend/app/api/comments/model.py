from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Text

from app.core.base_model import Base, TimeMixin


class Comment(Base, TimeMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("articles.id"), comment="所属文章ID")
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True, comment="父评论ID（回复）")
    nickname: Mapped[str] = mapped_column(String(25), comment="昵称")
    email: Mapped[str] = mapped_column(String(255), comment="邮箱，仅管理端可见")
    content: Mapped[str] = mapped_column(Text, comment="评论内容")