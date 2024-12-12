import http
import json

import requests
from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import (
    func,
    and_,
    extract,
    case,
)
from sqlalchemy.orm import Session, aliased
from starlette.requests import Request

from src.config.config import get_config
from src.dependencies.database_dependency import get_va_db
from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.forecasts.forecast_interface import IForecastRepository
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_order_configurations import OrderConfiguration
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

        dealer_submit = (
            self.get_va_db(request)
            .query(func.count().label("dealer_submit"))
            .select_from(Dealer)
            .join(Forecast, Dealer.id == Forecast.dealer_id)
            .filter(
                and_(
                    extract("month", Dealer.created_at) <= Forecast.month,
                    extract("year", Dealer.created_at) <= Forecast.year,
                )
            )
            .group_by(Forecast.month, Forecast.year)
            .subquery()
        )

        order_confirmation = (
            self.get_va_db(request)
            .query(func.count().label("total_oc"))
            .select_from(ForecastDetailMonth)
            .join(
                ForecastDetail,
                ForecastDetailMonth.forecast_detail_id == ForecastDetail.id,
            )
            .join(Forecast, ForecastDetail.forecast_id == Forecast.id)
            .filter(ForecastDetailMonth.confirmed_total_ws.isnot(None))
            .group_by(Forecast.month, Forecast.year)
            .subquery()
        )

        query = (
            self.get_va_db(request)
            .query(
                Forecast.month.label("month"),
                Forecast.year.label("year"),
                func.sum(dealer_submit.c.dealer_submit).label("dealer_submit"),
                (total_dealer - func.sum(dealer_submit.c.dealer_submit)).label(
                    "remaining_dealer_submit"
                ),
                func.sum(order_confirmation.c.total_oc).label("order_confirmation"),
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
        url = config.outbound["hoyu"].base_url + "/ords/hmsi/dealer_forcast/allocation"

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
                detail="Outbound Error: " + url + " " + json.dumps(payload),
            )
