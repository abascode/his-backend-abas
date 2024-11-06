from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: str
    name: str   

class SegmentResponse(BaseModel):
    id: str
    name: str
    category: CategoryResponse

class ModelResponse(BaseModel):
    id: str
    name: str
    segment: SegmentResponse