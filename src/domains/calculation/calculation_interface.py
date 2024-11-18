import abc

from fastapi import Request

from src.models.requests.calculation_request import (
    CalculationTemplateRequest,
    GetCalculationDetailRequest,
)
from src.models.responses.calculation_response import CalculationDetailResponse


class ICalculationUseCase:
    @abc.abstractmethod
    def generate_calculation_excel_template(
        self, request: Request, query_params: CalculationTemplateRequest
    ):
        pass

    def generate_excel_month_header(
        self, requested_config: CalculationTemplateRequest
    ) -> list[str]:
        pass

    def generate_excel_business_header(
        self, requested_config: CalculationTemplateRequest
    ) -> list[str]:
        pass

    def apply_excel_month_forecast_headers(
        self, business_header_entity: list[str], forecast_month_headers: list[str]
    ):
        pass

    def get_calculation_detail(
        self, request: Request, calculation_detail_request: GetCalculationDetailRequest
    ) -> CalculationDetailResponse:
        pass


class ICalculationRepository:
    pass
    # def finc_calculation(self, request: Request, month: int = 0, year: int = 0) -:
