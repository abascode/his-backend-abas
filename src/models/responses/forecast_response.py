from typing import TypeVar, Generic, List

from pydantic import BaseModel

class ForecastSummaryResponse(BaseModel):
    month: int
    year: int
    dealer_submit: 0
    remaining_dealer_submit: 0
    order_confirmation: 0