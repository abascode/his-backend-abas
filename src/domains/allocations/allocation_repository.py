from typing import List

from fastapi import Depends
from sqlalchemy import func, Integer, and_, cast, select, case, Float, text
from sqlalchemy.orm import Session, aliased
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.allocations.allocation_interface import IAllocationRepository
from src.domains.allocations.entities.allocation_approval_matrix import (
    AllocationApprovalMatrix,
)
from src.domains.allocations.entities.allocation_approvals import AllocationApproval
from src.domains.calculations.entities.va_slot_calculation_details import (
    SlotCalculationDetail,
)
from src.domains.calculations.entities.va_slot_calculations import SlotCalculation
from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.entities.va_models import Model
from src.domains.masters.entities.va_order_configurations import OrderConfiguration
from src.domains.masters.entities.va_stock_pilots import StockPilot
from src.models.requests.allocation_request import GetAllocationRequest


class AllocationRepository(IAllocationRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

    def get_allocation_adjustments(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ):

        forecast_detail_months_alias = aliased(ForecastDetailMonth)
        forecast_detail_alias = aliased(ForecastDetail)
        forecast_alias = aliased(Forecast)
        total_ws_alias = aliased(
            self.get_va_db(request)
            .query(
                func.sum(forecast_detail_months_alias.total_ws).label("total_ws_sum"),
                forecast_detail_alias.model_id.label("model_id"),
                forecast_detail_months_alias.forecast_month.label("forecast_month"),
                forecast_alias.year.label("year"),
                forecast_alias.month.label("month"),
            )
            .join(
                forecast_detail_alias,
                and_(
                    forecast_detail_alias.deletable == 0,
                    forecast_detail_alias.id
                    == forecast_detail_months_alias.forecast_detail_id,
                ),
            )
            .join(
                forecast_alias,
                and_(
                    forecast_alias.deletable == 0,
                    forecast_alias.id == forecast_detail_alias.forecast_id,
                ),
            )
            .filter(
                and_(
                    forecast_alias.month == get_allocation_request.month,
                    forecast_alias.year == get_allocation_request.year,
                    forecast_detail_months_alias.deletable == 0,
                )
            )
            .group_by(
                forecast_detail_months_alias.forecast_month,
                forecast_alias.year,
                forecast_alias.month,
                forecast_detail_alias.model_id,
            )
            .subquery()
        )

        query = (
            self.get_va_db(request)
            .query(
                ForecastDetailMonth.id,
                Dealer.id,
                Dealer.name,
                Forecast.year,
                Forecast.month,
                Model.id,
                Model.segment_id,
                Model.category_id,
                ForecastDetailMonth.forecast_month,
                func.coalesce(ForecastDetailMonth.adjustment, 0),
                func.coalesce(ForecastDetailMonth.total_ws, 0),
                case(
                    (
                        (
                            total_ws_alias.c.total_ws_sum > 0,
                            cast(func.coalesce(ForecastDetailMonth.total_ws, 0), Float)
                            / cast(
                                func.coalesce(total_ws_alias.c.total_ws_sum, 0), Float
                            )
                            * 100,
                        )
                    ),
                    else_=0,
                ),
                cast(
                    case(
                        (
                            (
                                total_ws_alias.c.total_ws_sum > 0,
                                cast(
                                    (
                                        (
                                            func.coalesce(
                                                SlotCalculationDetail.take_off, 0
                                            )
                                            + func.coalesce(SlotCalculationDetail.bo, 0)
                                        )
                                        * StockPilot.percentage
                                    )
                                    - (
                                        (
                                            func.coalesce(SlotCalculationDetail.soa, 0)
                                            + func.coalesce(SlotCalculationDetail.oc, 0)
                                            + func.coalesce(
                                                SlotCalculationDetail.booking_prospect,
                                                0,
                                            )
                                        )
                                        * func.coalesce(
                                            OrderConfiguration.forecast_percentage, 0
                                        )
                                        / 100
                                    ),
                                    Float,
                                )
                                / cast(
                                    func.coalesce(total_ws_alias.c.total_ws_sum, 0),
                                    Float,
                                )
                                * 100,
                            )
                        ),
                        else_=0,
                    ),
                    Integer,
                ),
                func.coalesce(ForecastDetailMonth.confirmed_total_ws, 0),
                func.coalesce(ForecastDetail.end_stock, 0),
            )
            .join(Dealer, and_(Dealer.id == Forecast.dealer_id))
            .join(
                ForecastDetail,
                and_(
                    ForecastDetail.forecast_id == Forecast.id,
                    ForecastDetail.deletable == 0,
                ),
            )
            .join(
                ForecastDetailMonth,
                and_(
                    ForecastDetailMonth.forecast_detail_id == ForecastDetail.id,
                    ForecastDetailMonth.deletable == 0,
                ),
            )
            .join(Model, and_(Model.id == ForecastDetail.model_id))
            .join(
                StockPilot,
                and_(
                    StockPilot.segment_id == Model.segment_id,
                    StockPilot.month == Forecast.month,
                    StockPilot.year == Forecast.year,
                ),
            )
            .join(
                OrderConfiguration,
                and_(
                    OrderConfiguration.month == Forecast.month,
                    OrderConfiguration.year == Forecast.year,
                    OrderConfiguration.category_id == Model.category_id,
                ),
            )
            .join(
                SlotCalculation,
                and_(
                    SlotCalculation.year == Forecast.year,
                    SlotCalculation.month == Forecast.month,
                    SlotCalculation.deletable == 0,
                ),
                isouter=True,
            )
            .join(
                SlotCalculationDetail,
                and_(
                    SlotCalculation.id == SlotCalculationDetail.slot_calculation_id,
                    SlotCalculationDetail.model_id == Model.id,
                    SlotCalculationDetail.forecast_month
                    == ForecastDetailMonth.forecast_month,
                    SlotCalculationDetail.deletable == 0,
                ),
                isouter=True,
            )
            .join(
                total_ws_alias,
                and_(
                    total_ws_alias.c.model_id == Model.id,
                    total_ws_alias.c.forecast_month
                    == ForecastDetailMonth.forecast_month,
                    total_ws_alias.c.model_id == Model.id,
                ),
                isouter=True,
            )
            .filter(
                and_(
                    Forecast.month == get_allocation_request.month,
                    Forecast.year == get_allocation_request.year,
                )
            )
            .group_by(
                Forecast.month,
                Forecast.year,
                Dealer.id,
                Model.id,
                Model.category_id,
                ForecastDetailMonth.forecast_month,
                ForecastDetailMonth.adjustment,
                ForecastDetailMonth.total_ws,
                total_ws_alias.c.total_ws_sum,
                SlotCalculationDetail.take_off,
                SlotCalculationDetail.soa,
                SlotCalculationDetail.oc,
                SlotCalculationDetail.bo,
                OrderConfiguration.forecast_percentage,
                StockPilot.percentage,
                ForecastDetailMonth.confirmed_total_ws,
                SlotCalculationDetail.booking_prospect,
                ForecastDetail.end_stock,
                ForecastDetailMonth.id,
            )
            .order_by(
                Model.id,
                Dealer.id,
            )
        )

        # print query with parameters
        print(query.statement.compile(compile_kwargs={"literal_binds": True}))

        res = query.all()

        return res

    def get_allocation_monthly_target(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ):
        query = (
            (
                self.get_va_db(request)
                .query(
                    MonthlyTargetDetail.category_id,
                    MonthlyTargetDetail.target,
                    MonthlyTargetDetail.dealer_id,
                    MonthlyTargetDetail.forecast_month,
                    func.coalesce(
                        func.sum(SlotCalculationDetail.soa + SlotCalculationDetail.bo),
                        0,
                    ),
                    func.coalesce(func.sum(ForecastDetailMonth.total_ws), 0),
                )
                .join(
                    MonthlyTarget,
                    and_(
                        MonthlyTarget.id == MonthlyTargetDetail.month_target_id,
                        MonthlyTarget.deletable == 0,
                    ),
                )
                .join(
                    Forecast,
                    and_(
                        Forecast.month == MonthlyTarget.month,
                        Forecast.year == MonthlyTarget.year,
                        Forecast.dealer_id == MonthlyTargetDetail.dealer_id,
                        Forecast.deletable == 0,
                    ),
                    isouter=True,
                )
                .join(
                    ForecastDetail,
                    and_(
                        ForecastDetail.forecast_id == Forecast.id,
                        ForecastDetail.deletable == 0,
                    ),
                    isouter=True,
                )
                .join(
                    Model,
                    and_(
                        Model.id == ForecastDetail.model_id,
                        Model.category_id == MonthlyTargetDetail.category_id,
                    ),
                )
                .join(
                    ForecastDetailMonth,
                    and_(
                        ForecastDetailMonth.forecast_detail_id == ForecastDetail.id,
                        ForecastDetailMonth.forecast_month
                        == MonthlyTargetDetail.forecast_month,
                        ForecastDetailMonth.deletable == 0,
                    ),
                )
                .join(
                    SlotCalculation,
                    and_(
                        SlotCalculation.month == MonthlyTarget.month,
                        SlotCalculation.year == MonthlyTarget.year,
                        SlotCalculation.deletable == 0,
                    ),
                )
                .join(
                    SlotCalculationDetail,
                    and_(
                        SlotCalculationDetail.slot_calculation_id == SlotCalculation.id,
                        SlotCalculationDetail.forecast_month
                        == MonthlyTargetDetail.forecast_month,
                        SlotCalculationDetail.deletable == 0,
                    ),
                )
            )
            .filter(
                and_(
                    MonthlyTarget.month == get_allocation_request.month,
                    MonthlyTarget.year == get_allocation_request.year,
                    MonthlyTargetDetail.deletable == 0,
                )
            )
            .group_by(
                MonthlyTargetDetail.category_id,
                MonthlyTargetDetail.target,
                MonthlyTargetDetail.dealer_id,
                MonthlyTargetDetail.forecast_month,
            )
        )

        rows = query.all()

        return rows

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

    def get_allocation_approvals(
        self, request: Request, month: int, year: int
    ) -> List[AllocationApproval]:
        pass

    def get_allocation_approval_matrices(
        self, request: Request
    ) -> List[AllocationApprovalMatrix]:
        pass

    def create_allocation_approvals(
        self, request: Request, approvals: List[AllocationApproval]
    ):
        pass
