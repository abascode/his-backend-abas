from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.forecast.entities.va_dealer_forecast import DealerForecast
from src.domains.forecast.forecast_interface import IForecastRepository


class ForecastRepository(IForecastRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

    def create_forecast(
        self, request: Request, forecast: DealerForecast
    ) -> DealerForecast:
        self.get_va_db(request).add(forecast)
        self.get_va_db(request).flush()
        return forecast

    def find_forecast(
        self, request: Request, forecast_id: str
    ) -> DealerForecast | None:
        return (
            self.get_va_db(request)
            .query(DealerForecast)
            .filter(DealerForecast.id == forecast_id, DealerForecast.deletable == 0)
            .first()
        )

    def delete_forecast(
        self, request: Request, forecast_id: str, hard_delete: bool = False
    ) -> None:
        data = self.find_forecast(request, forecast_id)
        if data is not None:
            if hard_delete:
                self.get_va_db(request).delete(data)
            else:
                data.deletable = 1
