from typing import List

from fastapi import Depends
from sqlalchemy import text, literal
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.forecast_interface import IForecastRepository
from src.models.requests.forecast_request import GetForecastSummaryRequest
from src.models.responses.forecast_response import GetForecastSummaryResponse
from src.shared.utils.pagination import paginate


class ForecastRepository(IForecastRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

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

    def create_forecast_detail(
        self, request: Request, forecast_detail: ForecastDetail
    ) -> None:
        self.get_va_db(request).add(forecast_detail)
        self.get_va_db(request).flush()

    def create_forecast_detail_month(
        self, request: Request, forecast_detail_month: ForecastDetailMonth
    ) -> None:
        self.get_va_db(request).add(forecast_detail_month)
        self.get_va_db(request).flush()

    def get_forecast_summary_response(
        self, request: Request, get_summary_request: GetForecastSummaryRequest
    ) -> tuple[List[GetForecastSummaryResponse], int]:
        query = self.get_va_db(request).query(
            Forecast.month.label("month"),
            Forecast.year.label("year"),
            literal(0).label("dealer_submit"),
            literal(0).label("remaining_dealer_submit"),
            literal(0).label("order_confirmation"),
        )

        res, cnt = paginate(
            query,
            get_summary_request.page,
            get_summary_request.size,
        )

        return [
            GetForecastSummaryResponse(
                year=year,
                month=month,
                dealer_submit=dealer_submit,
                remaining_dealer_submit=remaining_dealer_submit,
                order_confirmation=order_confirmation,
            )
            for year, month, dealer_submit, remaining_dealer_submit, order_confirmation in res
        ], cnt
