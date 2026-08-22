from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.articles.model import Article
from app.api.articles.schema import ArticleDetail, ArticleSummary
from app.core.denpendencies import db_getter

router = APIRouter(prefix="/common-articles", tags=["articles"])


@router.get("/articles")
async def get_articles(db: AsyncSession = Depends(db_getter)):
    stmt = select(Article).where(Article.status == "published").order_by(Article.created_at.desc())
    result = await db.execute(stmt)
    articles = result.scalars().all()
    data = [ArticleSummary.model_validate(article) for article in articles]
    return {"articles": data}


@router.get("/articles/{slug}")
async def get_article_detail(slug: str, db: AsyncSession = Depends(db_getter)):
    stmt = select(Article).where(Article.slug == slug, Article.status == "published")
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或尚未发布")
    return {"article": ArticleDetail.model_validate(article)}
