
from typing import List
from pydantic import BaseModel

from src.models.responses.master_response import ModelResponse, SegmentResponse


class GetCalculationStockPilotResponse(BaseModel):
    segment: SegmentResponse
    percentage: int

class GetCalculationDetailResponse(BaseModel):
    model: ModelResponse
    forecast_month: int
    take_off: int   
    bo: int
    soa: int
    oc: int
    booking_prospect: int

class GetCalculationResponse(BaseModel):
    id: str
    month: int
    year: int
    
    details: List[GetCalculationDetailResponse]
    stock_pilots: List[GetCalculationStockPilotResponse]
    

    
    
    
    
    