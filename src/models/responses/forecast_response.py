from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class ForecastSummaryResponse(BaseModel):
    month: int
    year: int
    dealer_submit: int
    remaining_dealer_submit: int
    order_confirmation: int