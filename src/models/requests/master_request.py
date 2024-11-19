from pydantic import BaseModel


class GetOrderConfigurationRequest(BaseModel):
    month: int
    year: int


class GetStockPilotRequest(BaseModel):
    month: int
    year: int