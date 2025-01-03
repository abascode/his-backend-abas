import http
import json

import requests
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import func, and_
from sqlalchemy.orm import Session, aliased
from starlette.requests import Request

from src.config.config import get_config
from src.dependencies.database_dependency import get_va_db
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
from src.domains.forecasts.forecast_interface import IForecastRepository
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model
from src.models.requests.forecast_request import (
    GetForecastSummaryRequest,
)
from src.models.responses.forecast_response import (
    GetForecastSummaryResponse,
)
from src.shared.utils.pagination import paginate


class ForecastRepository(IForecastRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

    def create_forecast(self, request: Request, forecast: Forecast) -> None:
        self.get_va_db(request).add(forecast)
        self.get_va_db(request).flush()

    def find_forecast(
        self,
        request: Request,
        forecast_id: str = None,
        dealer_id: str = None,
        month: int = None,
        year: int = None,
    ) -> Forecast | None:
        query = self.get_va_db(request).query(Forecast).filter(Forecast.deletable == 0)

        if forecast_id is not None:
            query = query.filter(Forecast.id == forecast_id)

        if dealer_id is not None:
            query = query.filter(Forecast.dealer_id == dealer_id)

        if month is not None:
            query = query.filter(Forecast.month == month)

        if year is not None:
            query = query.filter(Forecast.year == year)

        query = query.join(
            ForecastDetail,
            and_(
                ForecastDetail.forecast_id == Forecast.id, ForecastDetail.deletable == 0
            ),
        ).join(Model, and_(Model.id == ForecastDetail.model_id))

        return query.first()

    def get_forecast(
        self,
        request: Request,
        forecast_id: str = None,
        dealer_id: str = None,
        month: int = None,
        year: int = None,
    ) -> List[Forecast]:
        query = self.get_va_db(request).query(Forecast).filter(Forecast.deletable == 0)

        if forecast_id is not None:
            query = query.filter(Forecast.id == forecast_id)

        if dealer_id is not None:
            query = query.filter(Forecast.dealer_id == dealer_id)

        if month is not None:
            query = query.filter(Forecast.month == month)

        if year is not None:
            query = query.filter(Forecast.year == year)

        return query.all()

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

        total_dealer = (
            self.get_va_db(request).query(func.count(Dealer.id)).scalar_subquery()
        )

        forecast_alias = aliased(Forecast)

        dealer_submit = (
            self.get_va_db(request)
            .query(
                func.count(forecast_alias.dealer_id.distinct()).label("dealer_submit")
            )
            .filter(
                forecast_alias.deletable == 0,
                Forecast.year == forecast_alias.year,
                Forecast.month == forecast_alias.month,
            )
            .scalar_subquery()
        )

        order_confirmation = (
            self.get_va_db(request)
            .query(func.count(forecast_alias.dealer_id.distinct()).label("total_oc"))
            .join(
                ForecastDetail,
                and_(
                    forecast_alias.id == ForecastDetail.forecast_id,
                    ForecastDetail.deletable == 0,
                ),
            )
            .join(
                ForecastDetailMonth,
                and_(
                    ForecastDetailMonth.forecast_detail_id == ForecastDetail.id,
                    ForecastDetail.deletable == 0,
                ),
            )
            .filter(
                and_(
                    forecast_alias.deletable == 0,
                    forecast_alias.month == Forecast.month,
                    forecast_alias.year == Forecast.year,
                    ForecastDetailMonth.confirmed_total_ws.isnot(None),
                )
            )
            .scalar_subquery()
        )

        query = (
            self.get_va_db(request)
            .query(
                Forecast.month.label("month"),
                Forecast.year.label("year"),
                dealer_submit.label("dealer_submit"),
                (total_dealer - dealer_submit).label("remaining_dealer_submit"),
                order_confirmation.label("order_confirmation"),
            )
            .filter(Forecast.deletable == 0)
            .group_by(
                Forecast.month,
                Forecast.year,
            )
        )

        if (
            get_summary_request.month is not None
            and get_summary_request.year is not None
        ):
            query = query.filter(
                Forecast.month == get_summary_request.month,
                Forecast.year == get_summary_request.year,
            )

        query = query.order_by(Forecast.year.desc(), Forecast.month.desc())

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
            for month, year, dealer_submit, remaining_dealer_submit, order_confirmation in res
        ], cnt

    def add_forecast_archive(
        self,
        request: Request,
        forecast_archive: ForecastArchive,
        forecast_detail_archive: List[ForecastDetailArchive],
        forecast_detail_month_archive: List[ForecastDetailMonthArchive],
    ) -> None:
        self.get_va_db(request).add(forecast_archive)
        self.get_va_db(request).add_all(forecast_detail_archive)
        self.get_va_db(request).add_all(forecast_detail_month_archive)
        self.get_va_db(request).flush()

    def delete_forecast(self, request: Request, forecast: Forecast) -> None:
        for i in forecast.details:
            self.get_va_db(request).query(ForecastDetailMonth).filter(
                ForecastDetailMonth.forecast_detail_id.in_([i.id])
            ).delete()

        self.get_va_db(request).query(ForecastDetail).filter(
            ForecastDetail.forecast_id.in_([forecast.id])
        ).delete()

        self.get_va_db(request).query(Forecast).filter(
            and_(Forecast.id == forecast.id)
        ).delete()

        self.get_va_db(request).flush()
