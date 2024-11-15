import abc

from fastapi import Request

from src.models.requests.calculation_request import CalculationTemplateRequest

class ICalculationUseCase:
    @abc.abstractmethod
    
    def generate_calculation_excel_template(self, request: Request, query_params: CalculationTemplateRequest):
        pass
    
    def generate_excel_month_header(self, requested_config: CalculationTemplateRequest) -> list[str]:
        pass
    
    def generate_excel_business_header(self, requested_config: CalculationTemplateRequest) -> list[str]:
        pass
    
    def apply_excel_month_forecast_headers(self, business_header_entity: list[str],forecast_month_headers: list[str]):
        pass
    
class ICalculationRepository:
    pass