from typing import List

from pydantic import BaseModel

from src.models.responses.basic_response import TextValueResponse


class GetForecastSummaryResponse(BaseModel):
    year: int
    month: int
    dealer_submit: int
    remaining_dealer_submit: int
    order_confirmation: int


class GetForecastDetailMonthResponse(BaseModel):
    forecast_month: int
    total_rs: int
    total_ws: int
    final_allocation: int
    confirmed_total_ws: int


class GetForecastDetailResponse(BaseModel):
    id: str
    model: TextValueResponse
    months: List[GetForecastDetailMonthResponse]


class GetForecastResponse(BaseModel):
    id: str
    month: int
    year: int
    dealer: TextValueResponse
    models: List[GetForecastDetailResponse]


class GetApprovalAllocationSuccessResponse(BaseModel):
    primary_id: str
    status: str
    message: str


class GetApprovalAllocationErrorResponse(BaseModel):
    primary_id: str
    status: str
    message: str


class GetApprovalAllocationResponse(BaseModel):
    success_data: List[GetApprovalAllocationSuccessResponse]
    error_data: List[GetApprovalAllocationErrorResponse]
