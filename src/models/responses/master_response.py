from pydantic import BaseModel

from src.models.responses.basic_response import TextValueResponse


class StockPilotResponse(BaseModel):
    segment: TextValueResponse
    percentage: int
