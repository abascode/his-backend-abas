import abc

from starlette.requests import Request

from src.domains.forecast.entities.va_dealer_forecast import DealerForecast
from src.models.requests.forecast_request import UpsertForecastRequest
from src.models.responses.forecast_response import DealerForecastResponse


class IForecastUseCase:
    @abc.abstractmethod
    def upsert_forecast(
        self, request: Request, upsert_forecast_request: UpsertForecastRequest
    ) -> None:
        pass
    
    @abc.abstractmethod
    def find_forecast(
        self, request: Request, forecast_id: str
    ) -> DealerForecastResponse | None:
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
