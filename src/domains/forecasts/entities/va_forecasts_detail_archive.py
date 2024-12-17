from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship, Mapped
from datetime import datetime


class ForecastDetailArchive(BaseModel):
    __tablename__ = "va_forecast_details_archive"
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: MappedColumn[str] = mapped_column(String(255), nullable=True)
    forecast_id: MappedColumn[str] = mapped_column(String(255))
    model_id: MappedColumn[str] = mapped_column(String(255), nullable=True)
    end_stock: MappedColumn[int] = mapped_column(Integer, nullable=True)
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
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
