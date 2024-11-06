from datetime import datetime
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text


class Model(BaseModel):
    __tablename__ = "va_models"

    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    name: MappedColumn[str] = mapped_column(String(255), nullable=False)
    segment_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_segments.id"), nullable=False
    )
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
