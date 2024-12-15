from fastapi import Depends
from sqlalchemy import func, Integer, and_, cast, select, case, Float, text
from sqlalchemy.orm import Session, aliased
from starlette.requests import Request

from src.dependencies.database_dependency import get_va_db
from src.domains.allocations.allocation_interface import IAllocationRepository
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

        # forecast_detail_months_alias = aliased(ForecastDetailMonth)
        # total_ws = (
        #     self.get_va_db(request)
        #     .query(sum(forecast_detail_months_alias.total_ws))
        #     .correlate(Model, ForecastDetailMonth)
        # )
        #
        # """
        # CAST(CAST(coalesce((SELECT sum(va_forecast_detail_months_2.total_ws) AS sum_1
        #                          FROM va_forecast_detail_months AS va_forecast_detail_months_2
        #                          WHERE va_forecast_detail_months_2.forecast_month =
        #                                va_forecast_detail_months_1.forecast_month
        #                            AND
        #                              va_forecast_detail_months_2.forecast_detail_id IN (SELECT va_forecast_details_1.id
        #                                                                                 FROM va_forecast_details AS va_forecast_details_1,
        #                                                                                      va_models AS va_models_1
        #                                                                                 WHERE va_forecast_details_1.model_id = va_models_1.id
        #                                                                                   AND
        #                                                                                     va_forecast_details_1.forecast_id IN
        #                                                                                     (SELECT va_forecasts_2.id
        #                                                                                      FROM va_forecasts AS va_forecasts_2,
        #                                                                                           va_forecasts AS va_forecasts_1
        #                                                                                      WHERE va_forecasts_2.month = va_forecasts_1.month
        #                                                                                        AND va_forecasts_2.year = va_forecasts_1.year))),
        #                         0) AS FLOAT) AS FLOAT)
        # """
        #
        # query = (
        #     self.get_va_db(request)
        #     .query(
        #         Dealer.id,
        #         Dealer.name,
        #         Forecast.year,
        #         Forecast.month,
        #         Model.id,
        #         Model.segment_id,
        #         Model.category_id,
        #         ForecastDetailMonth.forecast_month,
        #         func.coalesce(ForecastDetailMonth.adjustment, 0),
        #         func.coalesce(ForecastDetailMonth.total_ws, 0),
        #     )
        #     .join(Dealer, and_(Dealer.id == Forecast.id))
        #     .join(
        #         ForecastDetail,
        #         and_(
        #             ForecastDetail.forecast_id == Forecast.id,
        #             ForecastDetail.deletable == 0,
        #         ),
        #     )
        #     .join(
        #         ForecastDetailMonth,
        #         and_(
        #             ForecastDetailMonth.forecast_detail_id == ForecastDetail.id,
        #             ForecastDetailMonth.deletable == 0,
        #         ),
        #     )
        #     .join(Model, and_(Model.id == ForecastDetail.model_id))
        #     .join(
        #         StockPilot,
        #         and_(
        #             StockPilot.segment_id == Model.segment_id,
        #             StockPilot.month == Forecast.month,
        #             StockPilot.year == Forecast.year,
        #         ),
        #     )
        #     .join(
        #         OrderConfiguration,
        #         and_(
        #             OrderConfiguration.month == Forecast.month,
        #             OrderConfiguration.year == Forecast.year,
        #             OrderConfiguration.category_id == Model.category_id,
        #         ),
        #     )
        #     .join(
        #         SlotCalculation,
        #         and_(
        #             SlotCalculation.year == Forecast.year,
        #             SlotCalculation.month == Forecast.month,
        #             SlotCalculation.deletable == 0,
        #         ),
        #         isouter=True,
        #     )
        #     .join(
        #         SlotCalculationDetail,
        #         and_(
        #             SlotCalculation.id == SlotCalculationDetail.slot_calculation_id,
        #             SlotCalculationDetail.model_id == Model.id,
        #             SlotCalculationDetail.forecast_month
        #             == ForecastDetailMonth.forecast_month,
        #             SlotCalculationDetail.deletable == 0,
        #         ),
        #         isouter=True,
        #     )
        #     .group_by(Forecast.month, Forecast.year)
        #     .order_by(
        #         Dealer.id,
        #         Model.category_id,
        #         Model.id,
        #         ForecastDetailMonth.forecast_month,
        #     )
        # ).all()

        query = """
select *, (unfinished_allocation * ws_percentage::double precision / 100)::int as allocation
from (select va_dealers .id                                                                                      as dealer_id,
             va_dealers.name                                                                                    as dealer,
             va_forecasts.year                                                                                  as year,
             va_forecasts.month                                                                                 as month,
             va_models.id                                                                                       as model_id,
             va_models.segment_id,
             va_models.category_id,
             va_forecast_detail_months.forecast_month,
             coalesce(va_forecast_detail_months.adjustment, 0)                                                  as adjustment,
             coalesce(va_forecast_detail_months.total_ws, 0)                                                    as ws,
             (coalesce((coalesce(va_forecast_detail_months.total_ws, 0)::DOUBLE PRECISION /
                        (NULLIF((select sum(coalesce(temp.total_ws, 0))
                                 from va_forecast_detail_months temp
                                 where temp.deletable = 0 and temp.forecast_month = va_forecast_detail_months.forecast_month
                                   and temp.forecast_detail_id in (select id
                                                                   from va_forecast_details vfd
                                                                   where vfd.model_id = va_models.id and vfd.deletable = 0
                                                                     and vfd.forecast_id in
                                                                         (select id
                                                                          from va_forecasts vf
                                                                          where vf.month = va_forecasts.month
                                                                            and vf.year = va_forecasts.year and vf.deletable = 0))),
                                0))::DOUBLE PRECISION), 0) *
              100)::int                                                                                         as ws_percentage,
             (((coalesce(take_off, 0) - coalesce(bo, 0)) * coalesce(va_stock_pilots.percentage, 0) -
               (coalesce(soa, 0) + coalesce(oc, 0) + coalesce(booking_prospect, 0))) * (coalesce(forecast_percentage,
                                                                                                 0)::DOUBLE PRECISION /
                                                                                        100)::double precision) as unfinished_allocation,
             coalesce(va_forecast_detail_months.confirmed_total_ws, 0)
      from va_forecasts
               left join va_dealers on va_dealers.id = va_forecasts.dealer_id
               left join va_forecast_details
                         on va_forecasts.id = va_forecast_details.forecast_id and va_forecast_details.deletable = 0
               left join va_forecast_detail_months
                         on va_forecast_details.id = va_forecast_detail_months.forecast_detail_id and
                            va_forecast_detail_months.deletable = 0
               left join va_models on va_forecast_details.model_id = va_models.id
               left join va_stock_pilots on va_stock_pilots.segment_id = va_models.segment_id and
                                            va_stock_pilots.month = va_forecasts.month and
                                            va_stock_pilots.year = va_forecasts.year
               left join va_slot_calculations
                         on va_slot_calculations.year = va_forecasts.year and
                            va_forecasts.month = va_slot_calculations.month and va_slot_calculations.deletable = 0
               left join va_order_configurations on va_order_configurations.month = va_forecasts.month and
                                                    va_order_configurations.year = va_forecasts.year and
                                                    va_order_configurations.category_id = va_models.category_id
               left join va_slot_calculation_details
                         on va_slot_calculations.id = va_slot_calculation_details.slot_calculation_id and
                            va_models.id = va_slot_calculation_details.model_id and
                            va_slot_calculation_details.forecast_month = va_forecast_detail_months.forecast_month and
                            va_slot_calculation_details.deletable = 0
      where va_forecasts.month = :month
        and va_forecasts.year = :year) base;
        """

        res = self.get_va_db(request).execute(
            text(query),
            {
                "month": get_allocation_request.month,
                "year": get_allocation_request.year,
            },
        )
        rows = res.fetchall()

        return rows

    def get_allocation_monthly_target(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ):
        query = """
select va_monthly_target_details.category_id,
       va_monthly_target_details.target,
       va_monthly_target_details.dealer_id,
       va_monthly_target_details.forecast_month,
       sum(soa + bo),
       coalesce(sum(total_ws), 0)
from va_monthly_targets
         join va_monthly_target_details on va_monthly_targets.id = va_monthly_target_details.month_target_id
         left join va_forecasts vf on vf.month = va_monthly_targets.month and va_monthly_targets.year = vf.year and
                                      vf.dealer_id = va_monthly_target_details.dealer_id
         left join va_forecast_details vfd on vfd.forecast_id = vf.id and vfd.deletable = 0
         left join va_models vm on vm.id = vfd.model_id and vm.category_id = va_monthly_target_details.category_id
         left join va_forecast_detail_months vfdm on vfdm.forecast_detail_id = vfd.id and
                                                     vfdm.forecast_month = va_monthly_target_details.forecast_month
         left join va_slot_calculations vsc
                   on vsc.month = va_monthly_targets.month and vsc.year = va_monthly_targets.year and vsc.deletable = 0
         left join va_slot_calculation_details vscd on vscd.slot_calculation_id = vsc.id and vscd.forecast_month =
                                                                                             va_monthly_target_details.forecast_month and
                                                       vscd.deletable = 0
where va_monthly_target_details.deletable = 0
  and va_monthly_targets.month = :month
  and va_monthly_targets.year = :year
group by va_monthly_target_details.category_id, va_monthly_target_details.target, va_monthly_target_details.dealer_id,
         va_monthly_target_details.forecast_month;
        """

        res = self.get_va_db(request).execute(
            text(query),
            {
                "month": get_allocation_request.month,
                "year": get_allocation_request.year,
            },
        )
        rows = res.fetchall()

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
