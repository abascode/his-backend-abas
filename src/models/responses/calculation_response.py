from typing import List

from pydantic import BaseModel


class CalculationDetailMonthResponse(BaseModel):
    month: int
    take_off: int
    bo: int
    soa: int
    oc: int
    booking_prospect: int


class CalculationDetailModelResponse(BaseModel):
    id: str
    name: str
    months: List[CalculationDetailMonthResponse]


class CalculationDetailResponse(BaseModel):
    models: List[CalculationDetailModelResponse]
