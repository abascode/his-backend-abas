from datetime import datetime
from typing import List

from src.domains.forecast.entities.va_dealer_forecast import DealerForecast
from src.domains.forecast.entities.va_dealer_forecast_month import DealerForecastMonth
from src.domains.master.entities.va_model import Model
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, relationship, MappedColumn
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class DealerForecastModel(BaseModel):
    __tablename__ = "va_dealer_forecast_model"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    dealer_forecast_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_dealer_forecast.id"), nullable=False
    )
    model_id: MappedColumn[str] = mapped_column(String(255), ForeignKey("va_models.id"), nullable=False)
    dealer_end_stock: MappedColumn[int] = mapped_column(Integer, nullable=False)
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
    
    forecast: MappedColumn[DealerForecast] = relationship(DealerForecast, back_populates="models")
    model: MappedColumn[Model] = relationship(Model)
    months: MappedColumn[List[DealerForecastMonth]] = relationship("DealerForecastMonth", back_populates="forecast_model")


@event.listens_for(DealerForecastModel, "before_insert")
def before_insert(mapper, connection, target: DealerForecastModel):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(DealerForecastModel, "before_update")
def before_update(mapper, connection, target: DealerForecastModel):
    target.updated_at = datetime.now()
