from typing import List

from sqlalchemy import event, ForeignKey

from sqlalchemy import DateTime, Integer, String, func, text, event
from src.shared.entities.basemodel import BaseModel
from src.shared.utils.xid import generate_xid

from sqlalchemy.orm import mapped_column, MappedColumn, relationship, Mapped
from datetime import datetime


class Forecast(BaseModel):
    __tablename__ = "va_forecasts"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    name: MappedColumn[str] = mapped_column(String(255), nullable=False)
    month: MappedColumn[int] = mapped_column(Integer, nullable=False)
    year: MappedColumn[int] = mapped_column(Integer, nullable=False)
    dealer_id: MappedColumn[str] = mapped_column(
        String(255), ForeignKey("va_dealers.id"), nullable=False
    )
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
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deletable: MappedColumn[int] = mapped_column(Integer, server_default=text("0"))

    details: Mapped[List["ForecastDetail"]] = relationship(
        "ForecastDetail", back_populates="forecast"
    )
    dealer: Mapped["Dealer"] = relationship("Dealer", back_populates="forecasts")


@event.listens_for(Forecast, "before_insert")
def before_insert(mapper, connection, target: Forecast):
    target.created_at = datetime.now()


@event.listens_for(Forecast, "before_update")
def before_update(mapper, connection, target: Forecast):
    target.updated_at = datetime.now()
