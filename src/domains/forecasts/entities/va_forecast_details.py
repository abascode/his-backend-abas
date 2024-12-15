from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text, event
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship, Mapped
from datetime import datetime


class ForecastDetail(BaseModel):
    __tablename__ = "va_forecast_details"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    forecast_id: MappedColumn[str] = mapped_column(
        String(255),
        ForeignKey("va_forecasts.id", onupdate="CASCADE"),
        nullable=False,
    )
    model_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_models.id", onupdate="CASCADE"), nullable=False
    )
    end_stock: MappedColumn[int] = mapped_column(Integer, nullable=False)
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
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))

    forecast: Mapped["Forecast"] = relationship("Forecast")
    months: Mapped[List["ForecastDetailMonth"]] = relationship("ForecastDetailMonth")
    model: Mapped["Model"] = relationship("Model")


@event.listens_for(ForecastDetail, "before_insert")
def before_insert(mapper, connection, target: ForecastDetail):
    target.created_at = datetime.now()


@event.listens_for(ForecastDetail, "before_update")
def before_update(mapper, connection, target: ForecastDetail):
    target.updated_at = datetime.now()
