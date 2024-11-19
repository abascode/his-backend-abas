
from src.shared.entities.basemodel import BaseModel
from src.shared.entities.basemodel import BaseModel

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship, Mapped
from datetime import datetime

from src.shared.utils.xid import generate_xid

class MonthlyTarget(BaseModel):
    __tablename__ = "va_monthly_targets"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    month: MappedColumn[int] = mapped_column(Integer, nullable=False)    
    year: MappedColumn[int] = mapped_column(Integer, nullable=False)
    
    created_by: MappedColumn[str] = mapped_column(
        String(255),
        nullable=True,
    )
    updated_by: MappedColumn[str] = mapped_column(
        String(255),
        nullable=True,
    )
    deleted_by: MappedColumn[str] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
    
    details: Mapped["MonthlyTargetDetail"] = relationship("MonthlyTargetDetail", back_populates="monthly_target")
    
@event.listens_for(MonthlyTarget, "before_insert")
def before_insert(mapper, connection, target: MonthlyTarget):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(MonthlyTarget, "before_update")
def before_update(mapper, connection, target: MonthlyTarget):
    target.updated_at = datetime.now()
    
