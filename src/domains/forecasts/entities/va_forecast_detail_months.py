from src.shared.entities.basemodel import BaseModel

from sqlalchemy import DateTime, ForeignKey, Integer, String, func, text
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn, relationship
from datetime import datetime


class ForecastDetailMonth(BaseModel):
    __tablename__ = "va_forecast_detail_months"
    id: MappedColumn[str] = mapped_column(String, primary_key=True, nullable=False)
    forecast_detail_id: MappedColumn[str] = mapped_column(String, ForeignKey("va_forecast_details.id"),nullable=False)
    forecast_month: MappedColumn[int] = mapped_column(String, nullable=False)
    rs_gov:  MappedColumn[int]  = mapped_column(Integer, nullable=False)
    ws_gov:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    rs_priv:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    ws_priv:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    total_rs:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    prev_rs_gov:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    prev_rs_priv:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    total_prev_rs:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    total_ws:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    total_prev_final_conf_allocation:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    new_ws_req:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    hmsi_allocation:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    adjustment:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_prev_final_ws_gov:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_prev_final_ws_priv:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_ws_gov:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_ws_priv:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_total_ws:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_final_gov:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_final_priv:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    confirmed_total_final_ws:  MappedColumn[int] = mapped_column(Integer, nullable=False)
    
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
    
    detail: MappedColumn["ForecastDetail"] = relationship("ForecastDetail", back_populates="months")
    