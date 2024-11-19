from typing import List

from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.forecast_interface import IForecastRepository


class ForecastRepository(IForecastRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return (
            request.state.va_db if request.state.va_db is not None else self.get_va_db
        )

    def create_forecast(self, request: Request, forecast: Forecast) -> None:
        self.get_va_db(request).add(forecast)
        self.get_va_db(request).flush()

    def find_forecast(self, request: Request, forecast_id: str) -> Forecast | None:
        return (
            self.get_va_db(request)
            .query(Forecast)
            .filter(Forecast.id == forecast_id)
            .first()
        )

    def bulk_create_forecast_detail(
        self, request: Request, forecast_details: List[ForecastDetail]
    ) -> None:
        self.get_va_db(request).add_all(forecast_details)
        self.get_va_db(request).flush()
