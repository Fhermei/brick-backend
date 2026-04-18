"""
Comments API Endpoints

Allows users to comment on tasks with threading support.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from src.core.security import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.models.project import Project
from src.models.task import Task
from src.models.comment import Comment
from src.schemas.comment import CommentCreate, CommentResponse

router = APIRouter()


@router.post("/tasks/{task_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    task_id: uuid.UUID,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a task"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if parent comment exists
    parent_id = comment_data.parent_id
    if parent_id:
        parent = db.query(Comment).filter(Comment.id == parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    
    # Create comment
    comment = Comment(
        task_id=task_id,
        user_id=user.id,
        body=comment_data.body,
        parent_id=parent_id
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Build response
    return CommentResponse(
        id=comment.id,
        task_id=comment.task_id,
        user_id=user.id,
        user_name=user.name,
        user_email=user.email,
        body=comment.body,
        parent_id=comment.parent_id,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=[]
    )


@router.get("/tasks/{task_id}/comments", response_model=List[CommentResponse])
async def get_task_comments(
    task_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a task with threading"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id, Task.is_deleted == False).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get all comments for this task
    comments = db.query(Comment).filter(
        Comment.task_id == task_id,
        Comment.parent_id == None
    ).order_by(Comment.created_at.asc()).all()
    
    def build_comment_tree(comment: Comment) -> CommentResponse:
        replies = db.query(Comment).filter(Comment.parent_id == comment.id).order_by(Comment.created_at.asc()).all()
        user_obj = db.query(User).filter(User.id == comment.user_id).first()
        
        return CommentResponse(
            id=comment.id,
            task_id=comment.task_id,
            user_id=comment.user_id,
            user_name=user_obj.name if user_obj else "Unknown",
            user_email=user_obj.email if user_obj else "unknown",
            body=comment.body,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            replies=[build_comment_tree(reply) for reply in replies]
        )
    
    return [build_comment_tree(comment) for comment in comments]


@router.delete("/comments/{comment_id}", status_code=status.HTTP_200_OK)
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only the author can delete)"""
    email = current_user.get("email") or current_user.get("username")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own comments")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}