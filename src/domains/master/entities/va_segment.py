from datetime import datetime
from src.domains.master.entities.va_categories import Category
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text


class Segment(BaseModel):
    __tablename__ = "va_segments"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    name : MappedColumn[str]= mapped_column(String(255), nullable=False)
    category_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_categories.id"), nullable=False
    )
    created_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: MappedColumn[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))
    percentage: MappedColumn[int] = mapped_column(Integer, nullable=False)
    month: MappedColumn[int] = mapped_column(Integer, nullable=False)
    year: MappedColumn[int] = mapped_column(Integer, nullable=False)

    category: MappedColumn[Category] = relationship(Category)
