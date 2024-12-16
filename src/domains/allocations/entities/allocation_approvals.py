from datetime import datetime
from typing import List

from sqlalchemy import (
    String,
    event,
    DateTime,
    Integer,
    Enum,
    ForeignKey,
    func,
    Text,
    text,
    and_,
)
from sqlalchemy.orm import mapped_column, relationship, Mapped

from src.domains.allocations.enums import AllocationApprovalFlagEnum
from src.shared.entities.basemodel import BaseModel
from src.shared.utils.xid import generate_xid


class AllocationApproval(BaseModel):
    __tablename__ = "va_allocation_approvals"
    id = mapped_column(String(255), primary_key=True)
    month = mapped_column(Integer, nullable=False)
    year = mapped_column(Integer, nullable=False)
    approver_id = mapped_column(String(255), ForeignKey("va_users.id"), nullable=True)
    approved_at = mapped_column(DateTime(timezone=True))
    approved_comment = mapped_column(Text, nullable=True)
    approval_flag = mapped_column(Enum(AllocationApprovalFlagEnum), nullable=False)
    role_id = mapped_column(Integer, nullable=False)
    division_id = mapped_column(Integer)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by = mapped_column(
        String(255),
        ForeignKey("va_users.id"),
        nullable=True,
    )
    updated_by = mapped_column(
        String(255),
        ForeignKey("va_users.id"),
        nullable=True,
    )
    # created_by_user = relationship("User", foreign_keys=[created_by])
    # approver = relationship("User", foreign_keys=[approver_id])
    # updated_by_user = relationship("User", foreign_keys=[updated_by])
    # deletable = mapped_column(Integer, server_default=text("0"))
    # deleted_at = mapped_column(DateTime(timezone=True), nullable=True)
    # deleted_by = mapped_column(
    #     String(255),
    #     ForeignKey("va_users.id"),
    #     nullable=True,
    # )


@event.listens_for(AllocationApproval, "before_insert")
def before_insert(mapper, connection, target: AllocationApproval):
    target.id = generate_xid()


@event.listens_for(AllocationApproval, "before_update")
def before_update(mapper, connection, target: AllocationApproval):
    target.updated_at = datetime.now()
