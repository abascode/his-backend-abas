from datetime import datetime

from src.domains.forecast.entities.va_dealer_forecast_model import DealerForecastModel
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import DateTime, ForeignKey, String, Integer, func, text, event

from src.shared.utils.xid import generate_xid


class DealerForecastMonth(BaseModel):
    __tablename__ = "va_dealer_forecast_months"

    id = mapped_column(String(255), primary_key=True, nullable=False)
    dealer_forecast_model_id = mapped_column(
        String(255), ForeignKey("va_dealer_forecast_model.id"), nullable=False
    )
    forecast_month = mapped_column(Integer, nullable=False)
    rs_gov = mapped_column(Integer, nullable=False)
    rs_priv = mapped_column(Integer, nullable=False)
    total_rs = mapped_column(Integer, nullable=False)
    prev_rs_gov = mapped_column(Integer, nullable=False)
    prev_rs_priv = mapped_column(Integer, nullable=False)
    total_prev_rs = mapped_column(Integer, nullable=False)
    ws_gov = mapped_column(Integer, nullable=False)
    ws_priv = mapped_column(Integer, nullable=False)
    total_ws = mapped_column(Integer, nullable=False)
    prev_final_ws_gov_conf = mapped_column(Integer, nullable=False)
    prev_final_ws_priv_conf = mapped_column(Integer, nullable=False)
    prev_final_confirm_allocation = mapped_column(Integer, nullable=False)
    new_ws_req = mapped_column(Integer, nullable=False)
    hmsi_allocation = mapped_column(Integer, nullable=False)
    ws_gov_conf = mapped_column(Integer, nullable=False)
    ws_priv_conf = mapped_column(Integer, nullable=False)
    total_ws_conf = mapped_column(Integer, nullable=False)
    final_ws_gov_conf = mapped_column(Integer, nullable=False)
    final_ws_priv_conf = mapped_column(Integer, nullable=False)
    total_final_ws_conf = mapped_column(Integer, nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    deletable = mapped_column(Integer, server_default=text("0"))
    forecast_model = relationship(DealerForecastModel, back_populates="months")


@event.listens_for(DealerForecastMonth, "before_insert")
def before_insert(mapper, connection, target: DealerForecastMonth):
    target.id = generate_xid()
    target.created_at = datetime.now()


@event.listens_for(DealerForecastMonth, "before_update")
def before_update(mapper, connection, target: DealerForecastMonth):
    target.updated_at = datetime.now()
