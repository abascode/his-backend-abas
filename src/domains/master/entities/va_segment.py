from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column
from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text


class Segment(BaseModel):
    __tablename__ = "va_segments"
    id = mapped_column(String(255), primary_key=True, nullable=False)
    name = mapped_column(String(255), nullable=False)
    category_id = mapped_column(
        String(255), ForeignKey("va_categories.id"), nullable=False
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable = mapped_column(Integer, server_default=text("0"))
