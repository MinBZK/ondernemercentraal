from fastapi import APIRouter, Depends, Query

import app.middleware.dependencies as deps
from app.controllers.comment import CommentController
from app.schemas.comment import Comment

router = APIRouter(tags=["comment"], prefix="/comment")


@router.post("/")
async def create_comment(
    comment_controller: CommentController = Depends(deps.get_comment_controller),
    content: str = Query(..., min_length=3, max_length=1024),
):
    await comment_controller.create_comment(content=content)


@router.get("/", response_model=list[Comment])
async def get_comments(
    comment_controller: CommentController = Depends(deps.get_comment_controller),
):
    return await comment_controller.get_comments()
