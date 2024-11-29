from typing import List
from pydantic import BaseModel

from src.models.responses.master_response import ModelResponse, SegmentResponse


class GetCalculationStockPilotResponse(BaseModel):
    segment: SegmentResponse
    percentage: int


class GetCalculationDetailResponse(BaseModel):
    month: int
    take_off: int
    bo: int
    soa: int
    oc: int
    booking_prospect: int


class GetCalculationDetailMonthsResponse(BaseModel):
    id: str
    name: str
    months: List[GetCalculationDetailResponse]


class GetCalculationResponse(BaseModel):
    models: List[GetCalculationDetailMonthsResponse]