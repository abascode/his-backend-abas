from pydantic import BaseModel


class GetForecastSummaryResponse(BaseModel):
    year: int
    month: int
    dealer_submit: int
    remaining_dealer_submit: int
    order_confirmation: int
