import math
from collections.abc import Sequence
from fastapi import APIRouter
from fastapi import status
from fastapi.params import Depends
from sqlalchemy import select, delete

from app.api.articles.model import Article
from app.api.comments.model import Comment
from app.core.denpendencies import db_getter, AsyncSession
from app.core.exceptions import CustomException
from app.common.response import SuccessResponse
from app.api.comments.schema import CommentSchema, CommentOutSchema
from app.core.denpendencies import get_current_user, limiter_request

router = APIRouter(prefix="/comments", tags=["文章评论"], dependencies=[Depends(limiter_request)])


@router.get("/{slug}")
async def get_comment_for_articles(slug: str,
                                   page: int = 1,
                                   size: int = 10,
                                   db: AsyncSession = Depends(db_getter)):
    result1 = await db.execute(select(Article.id).where(Article.slug == slug))
    article_id = result1.scalar_one_or_none()
    if not article_id:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, code=40401, message="该文章不存在")

    result2 = await db.execute(select(Comment).where(Comment.article_id == article_id)
                                              .order_by(Comment.parent_id.asc()))
    comments_all: Sequence[Comment] = result2.scalars().all()
    total_comment = len(comments_all)
    total_comment_pages = int(math.ceil(total_comment/size))
    if page > total_comment_pages:
        raise CustomException(message="该页数不存在", code=40401, status_code=status.HTTP_404_NOT_FOUND)
    offset = (page-1) * size

    nodes = {}
    for c in comments_all:
        nodes[c.id] = {
            "id": c.id,
            "article_id": c.article_id,
            "parent_id": c.parent_id,
            "nickname": c.nickname,
            "content": c.content,
            "created_at": c.created_at,
            "children": []
        }

    roots = []
    for c in comments_all:
        node = nodes[c.id]
        if c.parent_id is None:
            roots.append(node)
        else:
            parent = nodes.get(c.parent_id)
            if parent:
                parent["children"].append(node)
            else:
                roots.append(node)
    data = {
        "total_comment": total_comment,
        "total_comment_pages": total_comment_pages,
        "root": roots[offset:offset+size],
    }
    return SuccessResponse(data=data)


@router.post("/{slug}")
async def add_comment_for_article(slug: str, data: CommentSchema, db: AsyncSession = Depends(db_getter)):
    result = await db.execute(select(Article).where(Article.slug == slug, Article.status == "published"))
    article = result.scalar_one_or_none()
    if not article:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, message="该文章不存在", code=40401)
    data_dict = data.model_dump()
    data_dict["article_id"] = article.id
    comment = Comment(**data_dict)
    db.add(comment)
    article.comment_count += 1
    await db.flush()
    await db.refresh(comment)
    comment_out = CommentOutSchema.model_validate(comment)
    return SuccessResponse(data=comment_out, status_code=status.HTTP_200_OK)


@router.delete("/manage/{slug}/{id}")
async def del_comment_for_article(slug: str, id: int, _ = Depends(get_current_user),db: AsyncSession = Depends(db_getter)):
    comment = await db.get(Comment, id)
    if not comment:
        raise CustomException(status_code=status.HTTP_404_NOT_FOUND, code=40401, message="评论不存在")
    smtm = delete(Comment).where(Comment.id == id)
    await db.execute(smtm)
    return SuccessResponse(status_code=status.HTTP_200_OK)

