from pydantic import BaseModel


class OrderConfigurationsResponse(BaseModel):
    category_id: str
    forecast_percentage: int
    urgent_percentage: int

class StockPilotsResponse(BaseModel):
    segment_id: str
    percentage: int

