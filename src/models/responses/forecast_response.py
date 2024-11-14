from typing import TypeVar, Generic, List

import datetime
from typing import List
from pydantic import BaseModel
from src.models.responses.basic_response import TextValueResponse
from src.models.responses.master_response import ModelResponse


class ForecastSummaryResponse(BaseModel):
    month: int
    year: int
    dealer_submit: int
    remaining_dealer_submit: int
    order_confirmation: int


class DealerForecastMonthResponse(BaseModel):
    id: str
    dealer_forecast_model_id: str
    forecast_month: int
    rs_gov: int
    rs_priv: int
    total_rs: int
    prev_rs_gov: int
    prev_rs_priv: int
    total_prev_rs: int
    ws_gov: int
    ws_priv: int
    total_ws: int
    prev_final_ws_gov_conf: int
    prev_final_ws_priv_conf: int
    prev_final_confirm_allocation: int
    new_ws_req: int
    hmsi_allocation: int
    ws_gov_conf: int
    ws_priv_conf: int
    total_ws_conf: int
    final_ws_gov_conf: int
    final_ws_priv_conf: int
    total_final_ws_conf: int


class DealerForecastModelResponse(BaseModel):
    id: str
    dealer_forecast_id: str
    model: ModelResponse
    dealer_end_stock: int

    months: List[DealerForecastMonthResponse]


class DealerForecastResponse(BaseModel):
    id: str
    month: int
    year: int
    dealer_submit: int
    remaining_dealer_submit: int
    order_confirmation: int
