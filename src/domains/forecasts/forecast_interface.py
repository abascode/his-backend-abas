import abc
from typing import List

from fastapi import UploadFile
from starlette.requests import Request

from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
    ConfirmForecastRequest,
    ApprovalAllocationRequest,
)
from src.models.responses.forecast_response import (
    GetForecastSummaryResponse,
    GetForecastResponse,
    GetApprovalAllocationResponse,
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

    @abc.abstractmethod
    def upsert_monthly_target(
        self, request: Request, monthly_target_data: UploadFile, month: int, year: int
    ) -> None:
        pass

    @abc.abstractmethod
    def confirm_forecast(
        self, request: Request, confirm_request: ConfirmForecastRequest
    ):
        pass

    @abc.abstractmethod
    def approve_allocation(
            self, request: Request, approval_request: ApprovalAllocationRequest, month: int, year: int
    ):
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
    def find_monthly_target(
        self,
        request: Request,
        monthly_target_id: str = None,
        month: int = None,
        year: int = None,
    ) -> MonthlyTarget | None:
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

    def create_monthly_target(
        self, request: Request, monthly_target: MonthlyTarget
    ) -> MonthlyTarget:
        pass

    def create_monthly_target_detail(
        self, request: Request, monthly_target_detail: MonthlyTargetDetail
    ) -> MonthlyTargetDetail:
        pass

    @abc.abstractmethod
    def approve_allocation_data(
        self, request: Request, get_approve_allocation_request: ApprovalAllocationRequest
    ) -> GetApprovalAllocationResponse:
        pass