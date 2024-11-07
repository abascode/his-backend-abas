import http

from fastapi import Depends, HTTPException
from starlette.requests import Request

from src.domains.forecast.entities.va_dealer_forecast import DealerForecast
from src.domains.forecast.entities.va_dealer_forecast_model import DealerForecastModel
from src.domains.forecast.entities.va_dealer_forecast_month import DealerForecastMonth
from src.domains.forecast.forecast_interface import (
    IForecastUseCase,
    IForecastRepository,
)
from src.domains.forecast.forecast_repository import ForecastRepository
from src.domains.master.master_interface import IMasterRepository
from src.domains.master.master_repository import MasterRepository
from src.models.requests.forecast_request import UpsertForecastRequest
from src.shared.enums import Database
from src.shared.utils.database_utils import begin_transaction, commit


class ForecastUseCase(IForecastUseCase):
    def __init__(
        self,
        forecast_repo: IForecastRepository = Depends(ForecastRepository),
        master_repo: IMasterRepository = Depends(MasterRepository),
    ):
        self.forecast_repo = forecast_repo
        self.master_repo = master_repo

    def upsert_forecast(
        self, request: Request, upsert_forecast_request: UpsertForecastRequest
    ) -> None:
        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        self.forecast_repo.delete_forecast(request, upsert_forecast_request.id, True)

        dealer = self.master_repo.first_or_create_dealer(
            request, upsert_forecast_request.dealer_name
        )

        models = []

        for i in upsert_forecast_request.models:
            model = self.master_repo.find_model(request, name=i.model)
            if model is None:
                raise HTTPException(
                    status_code=http.HTTPStatus.BAD_REQUEST,
                    detail=f"Model {i.model} is not found",
                )

            months = [
                DealerForecastMonth(
                    forecast_month=j.forecast_month,
                    rs_gov=j.rs_gov,
                    rs_priv=j.rs_priv,
                    prev_final_confirm_allocation=j.prev_final_confirm_allocation,
                    prev_rs_gov=j.prev_rs_gov,
                    prev_rs_priv=j.prev_rs_priv,
                    ws_gov=j.ws_gov,
                    ws_priv=j.ws_priv,
                    prev_final_ws_gov_conf=j.prev_final_ws_gov_conf,
                    prev_final_ws_priv_conf=j.prev_final_ws_priv_conf,
                    new_ws_req=j.new_ws_req,
                    hmsi_allocation=j.hmsi_allocation,
                    ws_gov_conf=j.ws_gov_conf,
                    ws_priv_conf=j.ws_priv_conf,
                    final_ws_gov_conf=j.final_ws_gov_conf,
                    final_ws_priv_conf=j.final_ws_priv_conf,
                    total_rs=j.total_rs,
                    total_prev_rs=j.total_prev_rs,
                    total_ws=j.total_ws,
                    total_ws_conf=j.total_ws_conf,
                    total_final_ws_conf=j.total_final_ws_conf,
                )
                for j in i.months
            ]
            forecast_model = DealerForecastModel(
                model_id=model.id,
                dealer_end_stock=i.dealer_end_stock,
                months=months,
            )
            models.append(forecast_model)

        forecast = DealerForecast(
            id=upsert_forecast_request.id,
            month=upsert_forecast_request.month,
            year=upsert_forecast_request.year,
            dealer_id=dealer.id,
            models=models,
        )

        self.forecast_repo.create_forecast(request, forecast)

        commit(request, Database.VEHICLE_ALLOCATION)
        
    def get_forecast_summary(
        self, request: Request, get_forecast_summary_request: ForecastSummaryRequest
    ) -> tuple[List[ForecastSummaryResponse], int]:
        res, cnt = self.forecast_repo(request, get_forecast_summary_request)

        return [
            ForecastSummaryResponse(
                month= i.month,
                year= i.year,
                dealer_submit= i.dealer_submit,
                remaining_dealer_submit= i.remaining_dealer_submit,
                order_confirmation= i.order_confirmation,
            )
            for i in res
        ], cnt

