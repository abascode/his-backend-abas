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
    pass


class GetForecastDetailRequest(BaseModel):
    month: int
    year: int
    dealer_id: str

class ApprovalAllocationData(BaseModel):
    RECORD_ID: str
    DEALER_FORECAST_ID: str
    MODEL_VARIANT: str
    N0_HMSI_ALLOCATION: int
    N1_HMSI_ALLOCATION: int
    N2_HMSI_ALLOCATION: int
    N3_HMSI_ALLOCATION: int
    N4_HMSI_ALLOCATION: int

class ApprovalAllocationRequest(BaseModel):
    data: List[ApprovalAllocationData]