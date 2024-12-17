from typing import List
from pydantic import BaseModel

from src.models.responses.basic_response import TextValueResponse
from src.models.responses.master_response import ModelResponse, SegmentResponse


class GetCalculationStockPilotResponse(BaseModel):
    segment: SegmentResponse
    percentage: int


class GetCalculationDetailResponse(BaseModel):
    calculation_slot_id: str
    month: int
    take_off: int
    bo: int
    soa: int
    so: int
    oc: int
    booking_prospect: int
    slot_1: int | None
    slot_2: int | None


class GetCalculationDetailMonthsResponse(BaseModel):
    model_id: str
    segment: TextValueResponse
    category: TextValueResponse
    months: List[GetCalculationDetailResponse]


class GetCalculationResponse(BaseModel):
    models: List[GetCalculationDetailMonthsResponse]
