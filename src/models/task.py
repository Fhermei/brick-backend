"""
Task Model - Represents tasks within a project
"""

import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Date, Numeric, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False, default="task")
    priority = Column(String(20), nullable=False, default="medium")
    status = Column(String(50), nullable=False, default="todo")
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    date_assigned = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(Date, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    budget_allocated = Column(Numeric(15, 2), nullable=True, default=0)
    total_spent = Column(Numeric(15, 2), nullable=True, default=0)
    blocked_reason = Column(Text, nullable=True)
    custom_fields = Column(JSON, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships - NO backrefs to avoid conflicts
    project = relationship("Project", back_populates="tasks")
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    
    # Use foreign_keys only, no backrefs
    assignee_user = relationship("User", foreign_keys=[assigned_to])
    creator_user = relationship("User", foreign_keys=[created_by])
    
    expenses = relationship("Expense", back_populates="task", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    additional_assignees = relationship("TaskAssignee", back_populates="task", cascade="all, delete-orphan")
    budget_items = relationship("TaskBudgetItem", back_populates="task", cascade="all, delete-orphan")


class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_supervisor = Column(Boolean, default=False, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    task = relationship("Task", back_populates="additional_assignees")
    assignee_user = relationship("User", foreign_keys=[user_id])


class TaskBudgetItem(Base):
    __tablename__ = "task_budget_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    receipt_url = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    task = relationship("Task", back_populates="budget_items")
    submitter_user = relationship("User", foreign_keys=[user_id])
    approver_user = relationship("User", foreign_keys=[approved_by])