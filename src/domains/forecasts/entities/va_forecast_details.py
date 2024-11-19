from src.shared.entities.basemodel import BaseModel

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from datetime import datetime


class ForecastDetail(BaseModel):
    __tablename__ = "va_forecast_details"
    id: MappedColumn[str] = mapped_column(String, primary_key=True, nullable=False)
    forecast_id: MappedColumn[str] = mapped_column(
        String, ForeignKey("va_forecasts.id"), nullable=False
    )
    model_id: MappedColumn[str] = mapped_column(
        String, ForeignKey("va_models.id"), nullable=False
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

    forecast: MappedColumn["Forecast"] = relationship("Forecast")
    months: MappedColumn["ForecastDetailMonth"] = relationship("ForecastDetailMonth")
    model: MappedColumn["Model"] = relationship("Model")
