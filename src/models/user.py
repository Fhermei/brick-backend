import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    cognito_sub = Column(String(255), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Organization relationships - keep these
    owned_organizations = relationship(
        "Organization",
        back_populates="owner",
        foreign_keys="Organization.owner_id",
    )
    org_memberships = relationship(
        "OrgMember",
        back_populates="user",
    )
    
    # Project relationships
    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
    )
    created_projects = relationship(
        "Project",
        foreign_keys="Project.created_by",
        back_populates="creator"
    )
    
    # Task relationships - NO backrefs, just foreign_keys
    # These are read-only relationships to avoid conflicts
    assigned_tasks_list = relationship(
        "Task",
        foreign_keys="Task.assigned_to",
        viewonly=True
    )
    created_tasks_list = relationship(
        "Task",
        foreign_keys="Task.created_by",
        viewonly=True
    )
    
    # Expense relationships
    submitted_expenses = relationship(
        "Expense",
        foreign_keys="Expense.user_id",
        viewonly=True
    )
    approved_expenses = relationship(
        "Expense",
        foreign_keys="Expense.approved_by",
        viewonly=True
    )
    
    # Other relationships - viewonly to avoid conflicts
    comments = relationship(
        "Comment",
        foreign_keys="Comment.user_id",
        viewonly=True
    )
    notifications = relationship(
        "Notification",
        back_populates="user"
    )