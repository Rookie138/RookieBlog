"""baseline: 建出 user / articles / comments 三张表

Revision ID: 0001_baseline
Revises:
Create Date: 2026-09-19

这是项目**唯一且完整**的初始迁移，代表数据库的全部结构。
本项目早期有过迁移文件被误删（当时的 versions/ 目录被 .gitignore 忽略，导致文件也没进 git），
迁移链因此断档；这里做了一次「压平」：删除历史迁移，重新生成一条能覆盖全部表的基线。

约定（以后新增迁移请遵守）：
  1. versions/ 目录必须提交进 git（.gitignore 里不要忽略它），否则换机就丢表结构
  2. 一条迁移只做一件事，文件名用 `alembic revision --autogenerate -m "描述"` 生成
  3. 已有数据的表加列必须带 server_default，否则旧行会变成 NULL

校验方式（任何迁移改完都应该跑一次）：
  mysql -uroot -e "CREATE DATABASE blog_check DEFAULT CHARACTER SET utf8mb4;"
  # 把 DATABASE_NAME 指到空库后执行 alembic upgrade head，确认建表成功且与模型一致
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_baseline"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """建出全部三张表。顺序必须是 user → articles → comments（外键依赖）。"""

    # ---------------- user ----------------
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="用户ID"),
        sa.Column("username", sa.String(length=50), nullable=False, comment="用户账号"),
        sa.Column("name", sa.String(length=25), nullable=False, comment="昵称"),
        # 注释照搬现有库的写法：以后 autogenerate 才不会冒出无意义的 alter_column
        sa.Column("password", sa.String(length=255), nullable=False, comment="<PASSWORD>"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_time",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---------------- articles ----------------
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("slug", sa.String(length=50), nullable=False, comment="SEO友好链接"),
        sa.Column("title", sa.String(length=50), nullable=False, comment="标题"),
        sa.Column("summary", sa.String(length=255), nullable=True, comment="简介"),
        sa.Column("context", sa.Text(), nullable=False, comment="文章内容"),
        sa.Column("view_count", sa.Integer(), nullable=False, comment="文章观看次数"),
        sa.Column("comment_count", sa.Integer(), nullable=False, comment="评论数量"),
        sa.Column("status", sa.String(length=25), nullable=False, comment="文章状态"),
        sa.Column("author_id", sa.Integer(), nullable=False, comment="作者ID"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_time",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    # slug 必须唯一：否则并发写入会产生重复 slug，详情接口 scalar_one_or_none() 会直接抛错
    op.create_index("slug", "articles", ["slug"], unique=True)
    # 外键列索引（MySQL 建外键时会自动创建，这里显式声明以保持一致）
    op.create_index("author_id", "articles", ["author_id"], unique=False)

    # ---------------- comments ----------------
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, comment="主键ID"),
        sa.Column("article_id", sa.Integer(), nullable=False, comment="所属文章ID"),
        sa.Column("parent_id", sa.Integer(), nullable=True, comment="父评论ID（回复）"),
        sa.Column("nickname", sa.String(length=25), nullable=False, comment="昵称"),
        sa.Column("email", sa.String(length=255), nullable=False, comment="邮箱，仅管理端可见"),
        sa.Column("content", sa.Text(), nullable=False, comment="评论内容"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_time",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
            comment="更新时间",
        ),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["comments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("article_id", "comments", ["article_id"], unique=False)
    op.create_index("parent_id", "comments", ["parent_id"], unique=False)
    # 注意：这里刻意**不**建 ix_comments_id。模型里 Comment.id 只有 primary_key，
    # 主键本身已唯一且有序，再加一个唯一索引纯属浪费（旧库里那个 ix_comments_id 是早期
    # 模型写成 unique=True, index=True 留下的冗余产物）。基线以模型为准，不再复制这个索引。
    # 已有的库如果还残留该索引，不影响功能；想清掉可单独出一条迁移：
    #   op.drop_index("ix_comments_id", table_name="comments")


def downgrade() -> None:
    """按依赖反序删表。"""
    op.drop_index("parent_id", table_name="comments")
    op.drop_index("article_id", table_name="comments")
    op.drop_table("comments")

    op.drop_index("author_id", table_name="articles")
    op.drop_index("slug", table_name="articles")
    op.drop_table("articles")

    op.drop_table("user")
