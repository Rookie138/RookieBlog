"""数据库状态核对脚本（只读，不修改任何数据）。

用途：alembic_version 记录被清空后，先搞清楚"库里实际已经有什么"，
      再决定用 alembic stamp 还是 alembic upgrade，避免重复建表报错。

运行（在 backend 目录下）：
    uv run python check_db_state.py
或：
    .venv\\Scripts\\python.exe check_db_state.py

脚本只做 SELECT / SHOW，不会写入。核对完后可以删掉本文件。
"""
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.setting import settings

# Windows 控制台默认 GBK，输出 ✓/✗ 会抛 UnicodeEncodeError，这里强制 UTF-8
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# 模型期望存在的列（表名 -> 列名集合）
EXPECTED = {
    "user": {"id", "username", "name", "password", "created_at", "updated_time"},
    "articles": {
        "id", "slug", "title", "summary", "context",
        "view_count", "comment_count", "status", "author_id",
        "created_at", "updated_time",
    },
    "comments": {
        "id", "article_id", "parent_id", "nickname", "email",
        "content", "created_at", "updated_time",
    },
}


def p(line=""):
    sys.stderr.write(str(line) + "\n")


async def main() -> int:
    p("=" * 72)
    p(f"数据库: {settings.DATABASE_USER}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")
    p("=" * 72)

    engine = create_async_engine(settings.ASYNC_DB_URI)
    exit_code = 0
    try:
        async with engine.connect() as conn:
            # ---- 1. alembic_version ----
            p()
            p("[1] alembic_version 表")
            has_version_table = (
                await conn.execute(
                    text(
                        "SELECT COUNT(*) FROM information_schema.tables "
                        "WHERE table_schema = DATABASE() AND table_name = 'alembic_version'"
                    )
                )
            ).scalar()
            if not has_version_table:
                p("    ✗ 表不存在（说明 alembic 从未在此库执行过）")
                recorded = []
            else:
                recorded = [
                    r[0]
                    for r in (
                        await conn.execute(text("SELECT version_num FROM alembic_version"))
                    ).all()
                ]
                if not recorded:
                    p("    ! 表存在但没有任何记录（被清空过）")
                    p("      影响：alembic 认为「什么都没执行过」")
                else:
                    for v in recorded:
                        p(f"    记录: {v}")
            p("    当前磁盘上的迁移: 0001_baseline.py (down_revision=None, 建 user/articles/comments)")

            # ---- 2. 表清单 ----
            p()
            p("[2] 实际存在的表")
            tables = [
                r[0]
                for r in (
                    await conn.execute(
                        text(
                            "SELECT table_name FROM information_schema.tables "
                            "WHERE table_schema = DATABASE() ORDER BY table_name"
                        )
                    )
                ).all()
            ]
            for t in tables:
                p(f"    - {t}")
            for t in EXPECTED:
                if t not in tables:
                    p(f"    [缺失表] 模型期望但数据库没有: {t}")
                    exit_code = 1

            # ---- 3. 逐表核对列 ----
            p()
            p("[3] 列核对（ORM 期望 vs 数据库实际）")
            for table, expected_cols in EXPECTED.items():
                if table not in tables:
                    continue
                rows = (
                    await conn.execute(
                        text(
                            "SELECT column_name, column_type, is_nullable, column_default "
                            "FROM information_schema.columns "
                            "WHERE table_schema = DATABASE() AND table_name = :t "
                            "ORDER BY ordinal_position"
                        ),
                        {"t": table},
                    )
                ).all()
                actual = {r[0] for r in rows}
                p(f"    -- {table}")
                for name, ctype, nullable, default in rows:
                    p(f"       {name:14} {ctype:20} null={nullable:3} default={default}")
                missing = expected_cols - actual
                if missing:
                    p(f"       [缺失列] {sorted(missing)}")
                    exit_code = 1
                else:
                    p("       [列齐全]")

            # ---- 4. 索引核对 ----
            p()
            p("[4] 索引（重点看 articles.slug 是否唯一、comments 是否有查询用索引）")
            for table in ("articles", "comments"):
                if table not in tables:
                    continue
                idx = (
                    await conn.execute(
                        text(
                            "SELECT index_name, non_unique, column_name, seq_in_index "
                            "FROM information_schema.statistics "
                            "WHERE table_schema = DATABASE() AND table_name = :t "
                            "ORDER BY index_name, seq_in_index"
                        ),
                        {"t": table},
                    )
                ).all()
                p(f"    -- {table}")
                grouped: dict[str, list] = {}
                for name, non_unique, col, _seq in idx:
                    grouped.setdefault(name, []).append((col, non_unique))
                for name, cols in grouped.items():
                    uniq = "UNIQUE" if cols[0][1] == 0 else "index"
                    p(f"       {name:28} {uniq:6} ({', '.join(c for c, _ in cols)})")
                if table == "articles":
                    slug_unique = any(
                        cols[0][1] == 0 and len(cols) == 1 and cols[0][0] == "slug"
                        for cols in grouped.values()
                    )
                    p(f"       -> slug 唯一约束: {'有' if slug_unique else '没有 (需要补迁移)'}")
                    if not slug_unique:
                        exit_code = 1
                if table == "comments":
                    has_article_idx = any(
                        "article_id" in [c for c, _ in cols] for cols in grouped.values()
                    )
                    p(f"       -> article_id 有索引: {'有' if has_article_idx else '没有 (前台查询会全表扫)'}")
    finally:
        await engine.dispose()

    p()
    p("=" * 72)
    p("结论提示：")
    p("  · 三张表都在 + 列齐全 + slug 唯一  -> 库结构与模型一致，")
    p("    执行 `uv run alembic stamp 0001_baseline` 仅登记版本号，不要 upgrade")
    p("  · 缺 comments 表  -> 全新库场景，执行 `uv run alembic upgrade head`")
    p("  · 缺 articles 的列（view_count / comment_count）或 slug 唯一约束")
    p("    -> 说明该库是旧结构，需要单独补一个迁移，不要直接 stamp")
    p("  · 任何情况下都不要 `alembic downgrade`")
    p("=" * 72)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
