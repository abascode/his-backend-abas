from pydantic import BaseModel


class GetAllocationRequest(BaseModel):
    month: int
    year: int
