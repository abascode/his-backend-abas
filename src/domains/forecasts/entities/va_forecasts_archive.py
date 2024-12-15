from typing import List

from sqlalchemy import ForeignKey

from sqlalchemy import DateTime, Integer, String, func, text, event
from src.shared.entities.basemodel import BaseModel

from sqlalchemy.orm import mapped_column, MappedColumn, relationship, Mapped
from datetime import datetime


class ForecastArchive(BaseModel):
    __tablename__ = "va_forecasts_archive"
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: MappedColumn[str] = mapped_column(String(255), nullable=True)
    name: MappedColumn[str] = mapped_column(String(255), nullable=True)
    month: MappedColumn[int] = mapped_column(Integer, nullable=True)
    year: MappedColumn[int] = mapped_column(Integer, nullable=True)
    dealer_id: MappedColumn[str] = mapped_column(String(255), nullable=True)
    confirmed_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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
        DateTime(timezone=True), nullable=True
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
