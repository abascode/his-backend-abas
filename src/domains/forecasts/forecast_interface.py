import abc
from typing import List

from starlette.requests import Request

from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.models.requests.forecast_request import CreateForecastRequest


class IForecastUseCase:
    @abc.abstractmethod
    def create_forecast(
        self, request: Request, create_forecast_request: CreateForecastRequest
    ) -> None:
        pass


class IForecastRepository:
    @abc.abstractmethod
    def create_forecast(self, request: Request, forecast: Forecast) -> Forecast:
        pass

    @abc.abstractmethod
    def find_forecast(self, request: Request, forecast_id: str) -> Forecast | None:
        pass

    @abc.abstractmethod
    def bulk_create_forecast_detail(
        self, request: Request, forecast_details: List[ForecastDetail]
    ) -> None:
        pass
