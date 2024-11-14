from datetime import datetime

from sqlalchemy import String, Integer, func, DateTime, text
from sqlalchemy.orm import MappedColumn, mapped_column

from src.shared.entities.basemodel import BaseModel


class StockPilot(BaseModel):
    __tablename__ = "va_segments"
    segment_id: MappedColumn[str] = mapped_column(
        String(255), primary_key=True, nullable=False
    )
    month: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    year: MappedColumn[int] = mapped_column(Integer, primary_key=True)
    percentage: MappedColumn[int] = mapped_column(Integer, nullable=True)
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
