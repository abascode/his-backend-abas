from sqlalchemy import DateTime, Integer, String, func, text
from src.shared.entities.basemodel import BaseModel
from sqlalchemy.orm import mapped_column, MappedColumn
from datetime import datetime


class ForecastDetailMonthArchive(BaseModel):
    __tablename__ = "va_forecast_detail_months_archive"
    id: MappedColumn[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: MappedColumn[str] = mapped_column(String(255), nullable=True)
    forecast_detail_id: MappedColumn[str] = mapped_column(String(255), nullable=True)
    forecast_month: MappedColumn[int] = mapped_column(Integer, nullable=True)
    rs_gov: MappedColumn[int] = mapped_column(Integer, nullable=True)
    ws_gov: MappedColumn[int] = mapped_column(Integer, nullable=True)
    rs_priv: MappedColumn[int] = mapped_column(Integer, nullable=True)
    ws_priv: MappedColumn[int] = mapped_column(Integer, nullable=True)
    total_rs: MappedColumn[int] = mapped_column(Integer, nullable=True)
    prev_rs_gov: MappedColumn[int] = mapped_column(Integer, nullable=True)
    prev_rs_priv: MappedColumn[int] = mapped_column(Integer, nullable=True)
    total_prev_rs: MappedColumn[int] = mapped_column(Integer, nullable=True)
    total_ws: MappedColumn[int] = mapped_column(Integer, nullable=True)
    total_prev_final_conf_allocation: MappedColumn[int] = mapped_column(
        Integer, nullable=True
    )
    new_ws_req: MappedColumn[int] = mapped_column(Integer, nullable=True)
    hmsi_allocation: MappedColumn[int] = mapped_column(Integer, nullable=True)
    adjustment: MappedColumn[int] = mapped_column(Integer, nullable=True)
    confirmed_prev_final_ws_gov: MappedColumn[int] = mapped_column(
        Integer, nullable=True
    )
    confirmed_prev_final_ws_priv: MappedColumn[int] = mapped_column(
        Integer, nullable=True
    )
    confirmed_ws_gov: MappedColumn[int] = mapped_column(Integer, nullable=True)
    confirmed_ws_priv: MappedColumn[int] = mapped_column(Integer, nullable=True)
    confirmed_total_ws: MappedColumn[int] = mapped_column(Integer, nullable=True)
    confirmed_final_gov: MappedColumn[int] = mapped_column(Integer, nullable=True)
    confirmed_final_priv: MappedColumn[int] = mapped_column(Integer, nullable=True)
    confirmed_total_final_ws: MappedColumn[int] = mapped_column(Integer, nullable=True)

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
