import abc
from typing import List

from starlette.requests import Request

from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
)
from src.models.responses.forecast_response import (
    GetForecastSummaryResponse,
    GetForecastResponse,
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


class IForecastRepository:
    @abc.abstractmethod
    def create_forecast(self, request: Request, forecast: Forecast) -> Forecast:
        pass

    @abc.abstractmethod
    def find_forecast(
        self,
        request: Request,
        forecast_id: str,
        dealer_id: str = None,
        month: int = None,
        year: int = None,
    ) -> Forecast | None:
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
