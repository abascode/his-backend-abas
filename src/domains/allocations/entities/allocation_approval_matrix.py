from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    Integer,
    ForeignKey,
)
from sqlalchemy.orm import mapped_column, MappedColumn
from src.shared.entities.basemodel import BaseModel


class AllocationApprovalMatrix(BaseModel):
    __tablename__ = "va_allocation_approval_matrix"
    role_id: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    order: MappedColumn[int] = mapped_column(Integer)
