from datetime import datetime

from src.shared.entities.basemodel import BaseModel
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import mapped_column, MappedColumn, Mapped, relationship


class Dealer(BaseModel):
    __tablename__ = "va_dealers"
    id: MappedColumn[str] = mapped_column(String(255), primary_key=True, nullable=False)
    name: MappedColumn[str] = mapped_column(String(255), nullable=False)
    created_at: MappedColumn[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    forecasts: Mapped["Forecast"] = relationship("Forecast")
