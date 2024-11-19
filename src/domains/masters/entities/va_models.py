from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import MappedColumn, mapped_column, Mapped, relationship

from src.domains.masters.entities.va_categories import Category
from src.domains.masters.entities.va_segments import Segment
from src.shared.entities.basemodel import BaseModel


class Model(BaseModel):
    __tablename__ = "va_models"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True)
    manufacture_code: MappedColumn[str] = mapped_column(String(255))
    group: MappedColumn[str] = mapped_column(String(255))
    variant: MappedColumn[str] = mapped_column(String(255))
    category_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_categories.id")
    )
    segment_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_segments.id")
    )
    usage: MappedColumn[str] = mapped_column(String(255))
    euro: MappedColumn[str] = mapped_column(String(255))
    category: Mapped[Category] = relationship("Category")
    segment: Mapped[Segment] = relationship("Segment")

    forecast_details: Mapped["ForecastDetail"] = relationship(
        "ForecastDetail", back_populates="model"
    )
