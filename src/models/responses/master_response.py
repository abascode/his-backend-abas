from pydantic import BaseModel


class OrderConfigurationsResponse(BaseModel):
    category_id: str
    forecast_percentage: int
    urgent_percentage: int

class StockPilotsResponse(BaseModel):
    segment_id: str
    percentage: int
    
class CategoryResponse(BaseModel):
    id: str
    
class SegmentResponse(BaseModel):
    id: str
class ModelResponse(BaseModel):
    id: str
    manufacturer_code: str
    group: str
    category: CategoryResponse
    segment: SegmentResponse
    usage: str
    euro: str

