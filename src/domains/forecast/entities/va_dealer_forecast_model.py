from datetime import datetime

from src.domains.forecast.entities.va_dealer_forecast import DealerForecast
from src.domains.master.entities.va_model import Model
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class DealerForecastModel(BaseModel):
    __tablename__ = "va_dealer_forecast_model"
    id = mapped_column(String(255), primary_key=True, nullable=False)
    dealer_forecast_id = mapped_column(
        String(255), ForeignKey("va_dealer_forecast.id"), nullable=False
    )
    model_id = mapped_column(String(255), ForeignKey("va_models.id"), nullable=False)
    dealer_end_stock = mapped_column(Integer, nullable=False)
    created_by = mapped_column(
        String(255),
        nullable=True,
    )
    updated_by = mapped_column(
        String(255),
        nullable=True,
    )
    deleted_by = mapped_column(
        String(255),
        nullable=True,
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable = mapped_column(Integer, server_default=text("0"))
    forecast = relationship(DealerForecast, back_populates="models")
    model = relationship(Model)
    months = relationship("DealerForecastMonth", back_populates="forecast_model")


@event.listens_for(DealerForecastModel, "before_insert")
def before_insert(mapper, connection, target: DealerForecastModel):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(DealerForecastModel, "before_update")
def before_update(mapper, connection, target: DealerForecastModel):
    target.updated_at = datetime.now()
