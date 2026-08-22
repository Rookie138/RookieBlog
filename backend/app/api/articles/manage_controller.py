from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.articles.model import Article
from app.api.articles.schema import ArticleCreate, ArticleDetail, ArticleSummary, ArticleUpdate
from app.api.auth.model import User
from app.core.denpendencies import db_getter, get_current_user

router = APIRouter(prefix="/manage-articles", tags=["articles"])


@router.get("/articles")
async def get_articles(
    db: AsyncSession = Depends(db_getter),
    _: User = Depends(get_current_user),
):
    stmt = select(Article).where(Article.status != "deleted").order_by(Article.created_at.desc())
    result = await db.execute(stmt)
    articles = result.scalars().all()
    data = [ArticleSummary.model_validate(article) for article in articles]
    return {"data": data}


@router.get("/articles/{slug}")
async def get_article_detail(
    slug: str,
    db: AsyncSession = Depends(db_getter),
    _: User = Depends(get_current_user),
):
    stmt = select(Article).where(Article.slug == slug, Article.status != "deleted")
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return {"article": ArticleDetail.model_validate(article)}


@router.post("/articles")
async def create_article(
    article_data: ArticleCreate,
    db: AsyncSession = Depends(db_getter),
    current_user: User = Depends(get_current_user),
):
    exists = await db.execute(select(Article).where(Article.slug == article_data.slug))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="slug 已存在")

    article = Article(**article_data.model_dump(), author_id=current_user.id)
    db.add(article)
    await db.flush()
    await db.refresh(article)
    return {"article": ArticleDetail.model_validate(article)}


@router.put("/articles/{slug}")
async def update_article(
    slug: str,
    article_data: ArticleUpdate,
    db: AsyncSession = Depends(db_getter),
    _: User = Depends(get_current_user),
):
    stmt = select(Article).where(Article.slug == slug, Article.status != "deleted")
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    values = article_data.model_dump(exclude_unset=True)
    next_slug = values.get("slug")
    if next_slug and next_slug != slug:
        exists = await db.execute(select(Article).where(Article.slug == next_slug))
        if exists.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="slug 已存在")

    for key, value in values.items():
        setattr(article, key, value)

    await db.flush()
    await db.refresh(article)
    return {"article": ArticleDetail.model_validate(article)}


@router.delete("/articles/{slug}")
async def delete_article(
    slug: str,
    db: AsyncSession = Depends(db_getter),
    _: User = Depends(get_current_user),
):
    stmt = select(Article).where(Article.slug == slug, Article.status != "deleted")
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    article.status = "deleted"
    await db.flush()
    return {"ok": True}
