from datetime import datetime

from src.domains.master.entities.va_dealer import Dealer
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class DealerForecast(BaseModel):
    __tablename__ = "va_dealer_forecast"

    id = mapped_column(String(255), primary_key=True, nullable=False)
    month = mapped_column(Integer, nullable=False)
    year = mapped_column(Integer, nullable=False)
    dealer_id = mapped_column(String(255), ForeignKey("va_dealers.id"), nullable=False)
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
    dealer = relationship(Dealer)
    models = relationship("DealerForecastModel", back_populates="forecast")
    dealer_submit =mapped_column(Integer, nullable=False)
    remaining_dealer_submit=mapped_column(Integer, nullable=False)
    order_confirmation=mapped_column(Integer, server_default=text('0'))


@event.listens_for(DealerForecast, "before_insert")
def before_insert(mapper, connection, target: DealerForecast):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(DealerForecast, "before_update")
def before_update(mapper, connection, target: DealerForecast):
    target.updated_at = datetime.now()
