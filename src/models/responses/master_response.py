from pydantic import BaseModel


class OrderConfigurationsResponse(BaseModel):
    month: int
    year: int
    category_id: str
    forecast_percentage: int
    urgent_percentage: int

class StockPilotsResponse(BaseModel):
    month: int
    year: int
    segment_id: str
    percentage: int