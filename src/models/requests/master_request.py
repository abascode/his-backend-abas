from src.shared.entities.basemodel import BaseModel


class StockPilotRequest(BaseModel):
    month: int
    year: int
