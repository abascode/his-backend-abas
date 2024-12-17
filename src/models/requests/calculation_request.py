from pydantic import BaseModel


class GetCalculationRequest(BaseModel):
    month: int
    year: int


class UpdateCalculationRequest(BaseModel):
    slot_1: int | None
    slot_2: int | None
    slot_calculation_id: str
    model_id: str
    forecast_month: int
