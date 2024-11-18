from pydantic import BaseModel


class StockPilotRequest(BaseModel):
    month: int
    year: int
