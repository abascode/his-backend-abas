import http
import json

import requests
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import text, literal
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.config.config import get_config
from src.dependencies.database_dependency import get_va_db
from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.forecasts.forecast_interface import IForecastRepository
from src.models.requests.forecast_request import (
    GetForecastSummaryRequest,
    ApprovalAllocationRequest,
)
from src.models.responses.forecast_response import (
    GetForecastSummaryResponse,
    GetApprovalAllocationResponse,
    GetApprovalAllocationSuccessResponse,
    GetApprovalAllocationErrorResponse,
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

        return query.first()

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

    def find_forecast_detail(
        self, request: Request, month: int, year: int, dealer_id: str
    ) -> ForecastDetail | None:
        return (
            self.get_va_db(request)
            .query(ForecastDetail)
            .filter(
                ForecastDetail.forecast.month == month,
                ForecastDetail.forecast.year == year,
                ForecastDetail.dealer_id,
            )
        )

    def find_monthly_target(
        self,
        request: Request,
        monthly_target_id: str = None,
        month: str = None,
        year: int = None,
    ) -> MonthlyTarget | None:
        query = (
            self.get_va_db(request)
            .query(MonthlyTarget)
            .filter(MonthlyTarget.deletable == 0)
        )

        if monthly_target_id is not None:
            query = query.filter(MonthlyTarget.id == monthly_target_id)

        if month is not None:
            query = query.filter(MonthlyTarget.month == month)

        if year is not None:
            query = query.filter(MonthlyTarget.year == year)

        return query.first()

    def create_monthly_target(
        self, request, monthly_target: MonthlyTarget
    ) -> MonthlyTarget:
        self.get_va_db(request).add(monthly_target)
        self.get_va_db(request).flush()

        return monthly_target

    def create_monthly_target_detail(
        self, request, monthly_target_detail: MonthlyTargetDetail
    ):
        self.get_va_db(request).add(monthly_target_detail)
        self.get_va_db(request).flush()

    def approve_allocation_data(
        self,
        request: Request,
        month: int,
        year: int,
        payload: dict,
    ):
        config = get_config()
        url = config.outbound[
            "hoyu"
        ].base_url + "/ords/hmsi/dealer_forcast/allocation?month={}&year={}".format(
            month, year
        )

        response = requests.post(
            url,
            json=payload,
            auth=(
                config.outbound["hoyu"].username,
                config.outbound["hoyu"].password,
            ),
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Outbound Error: " + response.url,
            )
