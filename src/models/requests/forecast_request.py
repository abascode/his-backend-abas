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


class GetForecastSummaryRequest(TableRequest, BaseModel):
    pass
