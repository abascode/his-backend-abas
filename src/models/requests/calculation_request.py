from fastapi import Query
from pydantic import BaseModel, Field, validator
from typing import  List


class CalculationTemplateRequest(BaseModel):
    month: int
    year: int
    forecast: str = Query(..., example='test')
    
    @validator("forecast")
    def validate_forecast(cls, value):
        try:
            forecast_list = [int(x) for x in value.split(",")]
        except ValueError:
            raise ValueError("Forecast must be a comma-separated list of integers.")
        
        if not all(isinstance(x, int) for x in forecast_list):
            raise ValueError("All items in forecast must be integers.")
        
        return forecast_list 