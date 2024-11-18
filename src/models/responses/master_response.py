from pydantic import BaseModel

from src.models.responses.basic_response import TextValueResponse

class CategoryResponse(BaseModel):
    id: str
    name: str

class StockPilotResponse(BaseModel):
    segment: TextValueResponse
    percentage: int
class SegmentResponse(BaseModel):
    id: str
    name: str
    category: CategoryResponse

class ModelResponse(BaseModel):
    id: str
    name: str
    segment: SegmentResponse