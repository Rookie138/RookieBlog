from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from app.core.base_model import Base, TimeMixin


class User(Base, TimeMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), comment="用户账号")
    name: Mapped[str] = mapped_column(String(25), comment="昵称")
    password: Mapped[str] = mapped_column(String(255), comment="<PASSWORD>")

