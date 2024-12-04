from typing import List

from pydantic import BaseModel

from src.models.requests.basic_request import TableRequest


class CreateForecastRequest(BaseModel):
    record_id: str
    record_name: str
    dealer_name: str
    dealer_code: str
    year: int
    month: int
    details: List[dict]


class ConfirmForecastRequest(BaseModel):
    record_id: str
    order_confirmation_date: str
    data: List[dict]


class GetForecastSummaryRequest(TableRequest, BaseModel):
    month: int | None = None
    year: int | None = None


class GetForecastDetailRequest(BaseModel):
    month: int
    year: int
    dealer_id: str


class ApprovalAllocationRequest(BaseModel):
    month: int
    year: int
