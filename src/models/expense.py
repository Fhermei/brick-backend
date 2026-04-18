"""
Expense Model - Tracks expenses for tasks with approval workflow
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.db.session import Base


class ExpenseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CARD = "card"
    CHEQUE = "cheque"
    OTHER = "other"


class ExpenseCategory(str, enum.Enum):
    MATERIALS = "materials"
    TRAVEL = "travel"
    LABOR = "labor"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    TRAINING = "training"
    ADMIN = "admin"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    amount = Column(Numeric(15, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False, default=PaymentMethod.OTHER)
    category = Column(SQLEnum(ExpenseCategory), nullable=False, default=ExpenseCategory.OTHER)
    receipt_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    status = Column(SQLEnum(ExpenseStatus), nullable=False, default=ExpenseStatus.PENDING)
    rejection_reason = Column(Text, nullable=True)
    
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships - simple, no backref conflicts
    task = relationship("Task", back_populates="expenses")
    submitter = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])