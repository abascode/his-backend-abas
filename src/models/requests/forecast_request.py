from typing import List

from pydantic import BaseModel


class UpsertForecastModelMonthRequest(BaseModel):
    forecast_month: int
    rs_gov: int
    rs_priv: int
    prev_final_confirm_allocation: int
    prev_rs_gov: int
    prev_rs_priv: int
    ws_gov: int
    ws_priv: int
    prev_final_ws_gov_conf: int
    prev_final_ws_priv_conf: int
    new_ws_req: int
    hmsi_allocation: int
    ws_gov_conf: int
    ws_priv_conf: int
    final_ws_gov_conf: int
    final_ws_priv_conf: int
    total_rs: int
    total_prev_rs: int
    total_ws: int
    total_ws_conf: int
    total_final_ws_conf: int


class UpsertForecastModelRequest(BaseModel):
    model: str
    dealer_end_stock: int
    months: List[UpsertForecastModelMonthRequest]


class UpsertForecastRequest(BaseModel):
    id: str
    dealer_name: str
    month: int
    year: int
    models: List[UpsertForecastModelRequest]
    
class ForecastSummaryRequest(BaseModel):
    month: int
    year: int
    dealer_submit: int
    remaining_dealer_submit: int
    order_confirmation: int

class ForecastDetailRequest(BaseModel):
    dealer_id: str
    month: int
    year: int
