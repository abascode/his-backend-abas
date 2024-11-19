
from src.shared.entities.basemodel import BaseModel
from src.shared.entities.basemodel import BaseModel

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from datetime import datetime

class MonthlyTarget(BaseModel):
    __tablename__ = "va_monthly_targets"
    id: MappedColumn[str] = mapped_column(String, primary_key=True, nullable=False)
    month: MappedColumn[int] = mapped_column(String, nullable=False)    
    year: MappedColumn[int] = mapped_column(String, nullable=False)
    
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
    
    details: MappedColumn["MonthlyTargetDetail"] = relationship("MonthlyTargetDetail", back_populates="monthly_target")