"""
Expense Pydantic Schemas
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Expense amount")
    payment_method: str = Field("other", description="cash, bank_transfer, card, cheque, other")
    category: str = Field("other", description="materials, travel, labor, equipment, software, training, admin, other")
    description: Optional[str] = None
    receipt_url: Optional[str] = None


class ExpenseApprove(BaseModel):
    approved: bool = Field(True)


class ExpenseReject(BaseModel):
    rejection_reason: str = Field(..., min_length=1, description="Reason for rejection")


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    task_title: str
    project_id: uuid.UUID
    project_title: str
    user_id: uuid.UUID
    user_name: str
    amount: float
    payment_method: str
    category: str
    receipt_url: Optional[str]
    description: Optional[str]
    status: str
    rejection_reason: Optional[str]
    approved_by: Optional[uuid.UUID]
    approved_by_name: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    
    model_config = {"from_attributes": True}


class ExpenseListResponse(BaseModel):
    total: int
    expenses: list[ExpenseResponse]