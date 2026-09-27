import math

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.articles.model import Article
from app.api.articles.schema import ArticleCreate, ArticleDetail, ArticleSummary, ArticleUpdate
from app.api.auth.model import User
from app.core.denpendencies import db_getter, get_current_user

from app.common.response import SuccessResponse
from app.core.exceptions import CustomException

router = APIRouter(prefix="/manage-articles", tags=["articles"])


@router.get("/articles")
async def get_articles(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(db_getter),
    _: User = Depends(get_current_user),
):
    offset_articles = (page - 1) * size
    total_articles = (await db.execute(select(func.count()).select_from(Article))).scalar_one_or_none()
    if offset_articles > total_articles:
        raise CustomException(message="不存在该页数", code=40401, status_code=status.HTTP_404_NOT_FOUND)

    stmt = (
            select(Article).where(Article.status != "deleted")
                            .order_by(Article.created_at.desc())
                            .offset(offset_articles)
                            .limit(size)
    )
    result = await db.execute(stmt)
    articles = result.scalars().all()
    # total = len(articles)
    # total_pages = int(math.ceil(total / size))
    # if page > total_pages:
    #     raise CustomException(message="该页数不存在", code=40401, status_code=status.HTTP_404_NOT_FOUND)
    # offset = page * size

    data = {
        "total_pages":total_articles/size,
        "article":[ArticleSummary.model_validate(article) for article in articles]
    }
    # return {"data": data}
    return SuccessResponse(message="成功获取全部文章", data=data)

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
    # return {"article": ArticleDetail.model_validate(article)}
    data = {"article": ArticleDetail.model_validate(article)}
    return SuccessResponse(data=data)


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
    return SuccessResponse(data={"article": ArticleDetail.model_validate(article)})


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
    return SuccessResponse(data={"article": ArticleDetail.model_validate(article)})


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
    return SuccessResponse(message="删除成功")
