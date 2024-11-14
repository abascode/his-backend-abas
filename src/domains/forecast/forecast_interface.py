import abc
from typing import List

from starlette.requests import Request

from src.domains.forecast.entities.va_dealer_forecast import DealerForecast
from src.models.requests.forecast_request import (
    UpsertForecastRequest,
    ForecastSummaryRequest,
)
from src.models.responses.forecast_response import ForecastSummaryResponse


class IForecastUseCase:
    @abc.abstractmethod
    def upsert_forecast(
        self, request: Request, upsert_forecast_request: UpsertForecastRequest
    ) -> None:
        pass

    @abc.abstractmethod
    def get_forecast_summary(
        self, request: Request, get_forecast_summary_request: ForecastSummaryRequest
    ) -> tuple[List[ForecastSummaryResponse], int]:
        pass


class IForecastRepository:
    @abc.abstractmethod
    def create_forecast(
        self, request: Request, forecast: DealerForecast
    ) -> DealerForecast:
        pass

    @abc.abstractmethod
    def find_forecast(
        self, request: Request, forecast_id: str
    ) -> DealerForecast | None:
        pass

    @abc.abstractmethod
    def delete_forecast(
        self, request: Request, forecast_id: str, hard_delete: bool = False
    ) -> None:
        pass

    def get_forecast_summary(
        self, request: Request, forecast_summary_request: ForecastSummaryRequest
    ) -> tuple[list[ForecastSummaryResponse], int]:
        pass
