import http
import re
from typing import List, Dict

from fastapi import Depends, HTTPException
from starlette.requests import Request

from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.forecast_interface import (
    IForecastUseCase,
    IForecastRepository,
)
from src.domains.forecasts.forecast_repository import ForecastRepository
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.master_interface import IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.requests.forecast_request import CreateForecastRequest
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
        self, request: Request, create_forecast_request: CreateForecastRequest
    ) -> None:
        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        forecast = self.forecast_repo.find_forecast(
            request, create_forecast_request.record_id
        )
        dealer = self.master_repo.upsert_dealer(
            request,
            Dealer(
                id=create_forecast_request.dealer_code,
                name=create_forecast_request.dealer_name,
            ),
        )

        is_create = forecast is None

        if forecast is None:
            forecast = Forecast(details=[])

        forecast.id = create_forecast_request.record_id
        forecast.name = create_forecast_request.record_name
        forecast.dealer_id = dealer.id
        forecast.year = create_forecast_request.year
        forecast.month = create_forecast_request.month

        new_details: Dict[str, ForecastDetail] = {
            i.id: self.convert_request_to_detail(request, i)
            for i in create_forecast_request.details
        }

        new_detail_months: Dict[str, Dict[int, ForecastDetailMonth]] = {}

        for i in new_details.values():
            if i.forecast_id not in new_detail_months:
                new_detail_months[i.forecast_id] = {}

            for j in i.months:
                new_detail_months[i.forecast_id][j.month] = j

        if is_create:
            self.forecast_repo.create_forecast(request, forecast)
        else:
            current_details: Dict[str, ForecastDetail] = {
                i.id: i for i in forecast.details
            }
            current_detail_months: Dict[str, Dict[int, ForecastDetailMonth]] = {}
            for i in current_details.values():
                if i.forecast_id not in current_detail_months:
                    current_detail_months[i.forecast_id] = {}
                for j in i.months:
                    current_detail_months[i.forecast_id][j.month] = j

            for current_detail in current_details.values():
                if current_detail.id not in new_details:
                    current_detail.deletable = 1
                    for current_detail_month in current_detail.months:
                        current_detail_month.deletable = 1
                else:
                    for current_detail_month in current_detail.months:
                        if (
                            current_detail_month.month
                            not in new_detail_months[current_detail.id]
                        ):
                            current_detail_month.deletable = 1

            for new_detail in new_details.values():
                if new_detail.id in current_details:
                    current_details[new_detail.id].model_id = new_detail.model_id
                    current_details[new_detail.id].end_stock = new_detail.end_stock
                    for new_detail_month in new_detail.months:
                        if (
                            new_detail_month.month
                            in current_detail_months[new_detail.id]
                        ):
                            current_detail_month = current_detail_months[new_detail.id][
                                new_detail_month.month
                            ]
                            current_detail_month.forecast_month = (
                                new_detail_month.forecast_month
                            )
                            current_detail_month.rs_gov = new_detail_month.rs_gov
                            current_detail_month.ws_gov = new_detail_month.ws_gov
                            current_detail_month.rs_priv = new_detail_month.rs_priv
                            current_detail_month.ws_priv = new_detail_month.ws_priv
                            current_detail_month.total_rs = new_detail_month.total_rs
                            current_detail_month.prev_rs_gov = (
                                new_detail_month.prev_rs_gov
                            )
                            current_detail_month.prev_rs_priv = (
                                new_detail_month.prev_rs_priv
                            )
                            current_detail_month.total_prev_rs = (
                                new_detail_month.total_prev_rs
                            )
                            current_detail_month.total_ws = new_detail_month.total_ws
                            current_detail_month.total_prev_final_conf_allocation = (
                                new_detail_month.total_prev_final_conf_allocation
                            )
                            current_detail_month.new_ws_req = (
                                new_detail_month.new_ws_req
                            )
                            current_detail_month.hmsi_allocation = (
                                new_detail_month.hmsi_allocation
                            )
                        else:
                            self.forecast_repo.create_forecast_detail_month(
                                request, new_detail_month
                            )
                else:
                    self.forecast_repo.create_forecast_detail(request, new_detail)
        commit(request, Database.VEHICLE_ALLOCATION)

    def convert_request_to_detail(
        self, request: Request, detail: dict
    ) -> ForecastDetail:
        pattern = r"n(\d+)_(rs_gov|ws_gov|rs_priv|ws_priv|total_rs|prev_rs_gov|prev_rs_priv|total_prev_rs|total_ws|new_ws_req|hmsi_allocation)"
        months_map: Dict[str, ForecastDetailMonth] = {}
        for k, v in detail.items():
            match = re.match(pattern, k)
            if match:
                if match.group(1) not in months_map:
                    months_map[match.group(1)] = ForecastDetailMonth(
                        forecast_month=int(match.group(1))
                    )
                if match.group(2) == "rs_gov":
                    months_map[match.group(1)].rs_gov = v
                if match.group(2) == "ws_gov":
                    months_map[match.group(1)].ws_gov = v
                if match.group(2) == "rs_priv":
                    months_map[match.group(1)].rs_priv = v
                if match.group(2) == "ws_priv":
                    months_map[match.group(1)].ws_priv = v
                if match.group(2) == "total_rs":
                    months_map[match.group(1)].total_rs = v
                if match.group(2) == "prev_rs_gov":
                    months_map[match.group(1)].prev_rs_gov = v
                if match.group(2) == "prev_rs_priv":
                    months_map[match.group(1)].prev_rs_priv = v
                if match.group(2) == "total_prev_rs":
                    months_map[match.group(1)].total_prev_rs = v
                if match.group(2) == "total_ws":
                    months_map[match.group(1)].total_ws = v
                if match.group(2) == "new_ws_req":
                    months_map[match.group(1)].new_ws_req = v
                if match.group(2) == "hmsi_allocation":
                    months_map[match.group(1)].hmsi_allocation = v

        model = self.master_repo.find_model(request, detail["model_varian"])

        if model is None:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=f"Model {detail['model_varian']} not found",
            )

        return ForecastDetail(
            model_id=detail["model_varian"],
            end_stock=detail["end_stock"],
            id=detail["dealer_forecast_id"],
            months=[ForecastDetailMonth(**i) for i in months_map.values()],
        )
