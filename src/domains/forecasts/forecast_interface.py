import abc
from typing import List

from starlette.requests import Request

from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_forecasts_archive import ForecastArchive
from src.domains.forecasts.entities.va_forecasts_detail_archive import (
    ForecastDetailArchive,
)
from src.domains.forecasts.entities.va_forecasts_detail_month_archive import (
    ForecastDetailMonthArchive,
)
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
    ConfirmForecastRequest,
    ApprovalAllocationRequest,
)
from src.models.responses.forecast_response import (
    GetForecastSummaryResponse,
    GetForecastResponse,
    GetApprovalAllocationResponse,
    ConfirmPdfResponse,
)


class IForecastUseCase:
    @abc.abstractmethod
    def upsert_forecast(
        self, request: Request, create_forecast_request: CreateForecastRequest
    ) -> None:
        pass

    @abc.abstractmethod
    def get_forecast_summary(
        self, request: Request, query: GetForecastSummaryRequest
    ) -> tuple[List[GetForecastSummaryResponse], int]:
        pass

    @abc.abstractmethod
    def get_forecast_detail(
        self, request: Request, get_forecast_detail_request: GetForecastDetailRequest
    ) -> GetForecastResponse:
        pass

    @abc.abstractmethod
    def confirm_forecast(
        self, request: Request, confirm_request: ConfirmForecastRequest
    ) -> ConfirmPdfResponse:
        pass

    @abc.abstractmethod
    def approve_allocation(
        self, request: Request, approval_request: ApprovalAllocationRequest
    ) -> None:
        pass

    def generate_forecast_pdf(
        self, request: Request, get_pdf_request: GetForecastDetailRequest
    ) -> str:
        pass


class IForecastRepository:
    @abc.abstractmethod
    def create_forecast(self, request: Request, forecast: Forecast) -> Forecast:
        pass

    @abc.abstractmethod
    def find_forecast(
        self,
        request: Request,
        forecast_id: str = None,
        dealer_id: str = None,
        month: int = None,
        year: int = None,
    ) -> Forecast | None:
        pass

    @abc.abstractmethod
    def get_forecast(
        self,
        request: Request,
        forecast_id: str = None,
        dealer_id: str = None,
        month: int = None,
        year: int = None,
    ) -> List[Forecast] | None:
        pass

    @abc.abstractmethod
    def create_forecast_detail(
        self, request: Request, forecast_detail: ForecastDetail
    ) -> None:
        pass

    @abc.abstractmethod
    def create_forecast_detail_month(
        self, request: Request, forecast_detail_month: ForecastDetailMonth
    ) -> None:
        pass

    @abc.abstractmethod
    def get_forecast_summary_response(
        self, request: Request, query: GetForecastSummaryRequest
    ) -> tuple[List[GetForecastSummaryResponse], int]:
        pass

    @abc.abstractmethod
    def add_forecast_archive(
        self,
        request: Request,
        forecast_archive: ForecastArchive,
        forecast_detail_archive: List[ForecastDetailArchive],
        forecast_detail_month_archive: List[ForecastDetailMonthArchive],
    ) -> None:
        pass

    @abc.abstractmethod
    def delete_forecast(self, request: Request, forecast: Forecast) -> None:
        pass
