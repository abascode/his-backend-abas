from pydantic import BaseModel


class GetCalculationRequest(BaseModel):
    month: int
    year: int