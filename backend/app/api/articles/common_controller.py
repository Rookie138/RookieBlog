import math

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.articles.model import Article
from app.api.articles.schema import ArticleDetail, ArticleSummary
from app.core.denpendencies import db_getter, limiter_request

from app.common.response import SuccessResponse
from app.core.exceptions import CustomException

router = APIRouter(prefix="/common-articles", tags=["articles"], dependencies=[Depends(limiter_request)])


@router.get("/articles")
async def get_articles(page:int = 1, size:int = 10, db: AsyncSession = Depends(db_getter)):
    offset_article = (page - 1) * size
    total_articles = (await db.execute(select(func.count()).select_from(Article))).scalar_one_or_none()

    if offset_article > total_articles:
        raise CustomException(message="不存在该页数", code=40401, status_code=status.HTTP_404_NOT_FOUND)
    stmt = (
        select(Article).where(Article.status == "published")
                            .order_by(Article.created_at.desc())
                            .offset(offset_article)
                            .limit(size)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    # total = len(articles)
    # total_pages = int(math.ceil(total / float(size)))
    # if page > total_pages:
    #     raise CustomException(message="该页数不存在", code=40401, status_code=status.HTTP_404_NOT_FOUND)


    data = {"total":total_articles,
            "total_pages":total_articles/size,
            "articles":[ArticleSummary.model_validate(article) for article in articles]}
    # return {"articles": data}
    return SuccessResponse(message="成功获取全部文章", data=data)

@router.get("/articles/{slug}")
async def get_article_detail(slug: str, db: AsyncSession = Depends(db_getter)):
    stmt = select(Article).where(Article.slug == slug, Article.status == "published")
    result = await db.execute(stmt)
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在或尚未发布")
    # return {"article": ArticleDetail.model_validate(article)}

    article.view_count += 1
    await db.flush()
    await db.refresh(article)

    data = {"article": ArticleDetail.model_validate(article)}
    return SuccessResponse(message=f"成功获取文章{slug}", data=data)
