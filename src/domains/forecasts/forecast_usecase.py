import http
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re
from typing import List, Dict

from fastapi import Depends, HTTPException, UploadFile
import openpyxl
from starlette.requests import Request

from src.domains.calculations.calculation_interface import ICalculationRepository
from src.domains.calculations.calculation_repository import CalculationRepository
from src.domains.forecasts.entities.va_forecast_detail_months import ForecastDetailMonth
from src.domains.forecasts.entities.va_forecast_details import ForecastDetail
from src.domains.forecasts.entities.va_forecasts import Forecast
from src.domains.forecasts.entities.va_forecasts_archive import ForecastArchive
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.forecasts.forecast_interface import (
    IForecastUseCase,
    IForecastRepository,
)
from src.domains.forecasts.forecast_repository import ForecastRepository
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.master_interface import IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.requests.allocation_request import GetAllocationRequest
from src.models.requests.forecast_request import (
    CreateForecastRequest,
    GetForecastSummaryRequest,
    GetForecastDetailRequest,
    ConfirmForecastRequest,
    ApprovalAllocationRequest,
)
from src.models.responses.allocation_response import (
    GetAllocationAdjustmentResponse,
    AllocationAdjustmentModelResponse,
    AllocationAdjustmentMonthResponse,
)
from src.models.responses.basic_response import TextValueResponse
from src.models.responses.forecast_response import (
    GetForecastSummaryResponse,
    GetForecastResponse,
    GetForecastDetailResponse,
    GetForecastDetailMonthResponse,
)
from src.shared.enums import Database
from src.shared.utils.database_utils import begin_transaction, commit
from src.shared.utils.date import get_month_difference, is_date_string_format
from src.shared.utils.excel import get_header_column_index
from src.shared.utils.file_utils import (
    clear_directory,
    get_file_extension,
    save_upload_file,
)
from src.shared.utils.xid import generate_xid


class ForecastUseCase(IForecastUseCase):

    def __init__(
        self,
        forecast_repo: IForecastRepository = Depends(ForecastRepository),
        master_repo: IMasterRepository = Depends(MasterRepository),
        calculation_repo: ICalculationRepository = Depends(CalculationRepository),
    ):
        self.forecast_repo = forecast_repo
        self.master_repo = master_repo
        self.calculation_repo = calculation_repo

    def upsert_forecast(
        self, request: Request, create_forecast_request: CreateForecastRequest
    ) -> None:
        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        forecast = self.forecast_repo.get_forecast(
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
            forecast = Forecast()

        forecast.id = create_forecast_request.record_id
        forecast.name = create_forecast_request.record_name
        forecast.dealer_id = dealer.id
        forecast.year = create_forecast_request.year
        forecast.month = create_forecast_request.month

        new_details: Dict[str, ForecastDetail] = {
            i["record_id"]: self.convert_request_to_detail(request, i)
            for i in create_forecast_request.details
        }

        new_detail_months: Dict[str, Dict[int, ForecastDetailMonth]] = {}

        for i in new_details.values():
            if i.id not in new_detail_months:
                new_detail_months[i.id] = {}

            for j in i.months:
                new_detail_months[i.id][j.forecast_month] = j

        if is_create:
            forecast.details = list(new_details.values())
            self.forecast_repo.create_forecast(request, forecast)
        else:
            current_details: Dict[str, ForecastDetail] = {
                i.id: i for i in forecast.details
            }
            current_detail_months: Dict[str, Dict[int, ForecastDetailMonth]] = {}
            for i in current_details.values():
                if i.id not in current_detail_months:
                    current_detail_months[i.id] = {}
                for j in i.months:
                    current_detail_months[i.id][j.forecast_month] = j

            for current_detail in current_details.values():
                if current_detail.id not in new_details:
                    current_detail.deletable = 1
                    for current_detail_month in current_detail.months:
                        current_detail_month.deletable = 1
                else:
                    for current_detail_month in current_detail.months:
                        if (
                            current_detail_month.forecast_month
                            not in new_detail_months[current_detail.id]
                        ):
                            current_detail_month.deletable = 1

            for new_detail in new_details.values():
                if new_detail.id in current_details:
                    current_details[new_detail.id].model_id = new_detail.model_id
                    current_details[new_detail.id].end_stock = new_detail.end_stock
                    for new_detail_month in new_detail.months:
                        if (
                            new_detail_month.forecast_month
                            in current_detail_months[new_detail.id]
                        ):
                            current_detail_month = current_detail_months[new_detail.id][
                                new_detail_month.forecast_month
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
                            print(
                                new_detail_month.forecast_month,
                                new_detail_month.forecast_detail_id,
                            )

                            self.forecast_repo.create_forecast_detail_month(
                                request, new_detail_month
                            )
                else:
                    new_detail.forecast_id = forecast.id
                    self.forecast_repo.create_forecast_detail(request, new_detail)
        commit(request, Database.VEHICLE_ALLOCATION)

    def get_forecast_summary(
        self, request: Request, query: GetForecastSummaryRequest
    ) -> tuple[List[GetForecastSummaryResponse], int]:
        data, total_count = self.forecast_repo.get_forecast_summary_response(
            request, query
        )

        return data, total_count

    def convert_request_to_detail(
        self, request: Request, detail: dict
    ) -> ForecastDetail:
        pattern = r"n(\d+)_(rs_gov|ws_gov|rs_priv|ws_priv|total_rs|prev_rs_gov|prev_rs_priv|total_prev_rs|total_ws|new_ws_req|hmsi_allocation)$"
        months_map: Dict[str, ForecastDetailMonth] = {}
        for k, v in detail.items():
            match = re.match(pattern, k)
            if match:
                if match.group(1) not in months_map:
                    months_map[match.group(1)] = ForecastDetailMonth(
                        forecast_month=int(match.group(1)),
                        forecast_detail_id=detail["dealer_forecast_id"],
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

        model = self.master_repo.find_model(request, detail["model_variant"])

        if model is None:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=f"Model {detail['model_variant']} not found",
            )

        return ForecastDetail(
            model_id=detail["model_variant"],
            end_stock=detail["end_stock"],
            id=detail["record_id"],
            months=[i for i in months_map.values()],
        )

    def get_forecast_detail(
        self, request: Request, get_forecast_detail_request: GetForecastDetailRequest
    ) -> GetForecastResponse:
        data = self.forecast_repo.find_forecast(
            request,
            month=get_forecast_detail_request.month,
            year=get_forecast_detail_request.year,
            dealer_id=get_forecast_detail_request.dealer_id,
        )

        if data is None:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND, detail="Forecast is not found"
            )

        models: List[GetForecastDetailResponse] = []

        for i in data.details:
            months = []

            for j in i.months:
                months.append(
                    GetForecastDetailMonthResponse(
                        forecast_month=j.forecast_month,
                        total_rs=j.total_rs,
                        total_ws=j.total_ws,
                        final_allocation=(
                            0 if j.hmsi_allocation is None else j.hmsi_allocation
                        ),
                        confirmed_total_ws=(
                            0 if j.confirmed_total_ws is None else j.confirmed_total_ws
                        ),
                    )
                )

            models.append(
                GetForecastDetailResponse(
                    id=i.id,
                    model=TextValueResponse(
                        text=i.model.id,
                        value=i.model.id,
                    ),
                    months=months,
                )
            )

        return GetForecastResponse(
            id=data.id,
            month=data.month,
            year=data.year,
            dealer=TextValueResponse(text=data.dealer.name, value=data.dealer.id),
            models=models,
        )

    def confirm_forecast(
        self, request: Request, confirm_request: ConfirmForecastRequest
    ):
        begin_transaction(request, Database.VEHICLE_ALLOCATION)
        forecast = self.forecast_repo.find_forecast(request, confirm_request.record_id)

        if forecast is None:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail="Forecast not found",
            )
        input_format = "%m/%d/%Y"
        date_obj = datetime.strptime(
            confirm_request.order_confirmation_date, input_format
        )
        utc_plus_7 = timezone(timedelta(hours=7))
        date_obj = date_obj.replace(tzinfo=utc_plus_7)

        forecast.confirmed_at = date_obj
        forecast.is_confirmed = True

        detail_map = {}
        for detail in forecast.details:
            detail_map[detail.id] = detail

        for request_detail in confirm_request.data:
            if request_detail["record_id"] in detail_map:
                i = detail_map[request_detail["record_id"]]
                if i.model_id == request_detail["model_variant"]:
                    pattern = r"n(\d+)_(ws_gov_conf|ws_priv_conf|total_ws_conf)"
                    detail_months_map = {}
                    for k, v in request_detail.items():
                        match = re.match(pattern, k)
                        if match:
                            if match.group(1) not in detail_months_map:
                                detail_months_map[match.group(1)] = {}
                            if match.group(2) == "ws_gov_conf":
                                detail_months_map[match.group(1)]["ws_gov_conf"] = v
                            if match.group(2) == "ws_priv_conf":
                                detail_months_map[match.group(1)]["ws_priv_conf"] = v
                            if match.group(2) == "total_ws_conf":
                                detail_months_map[match.group(1)]["total_ws_conf"] = v

                    for j in detail_map[request_detail["record_id"]].months:
                        if str(j.forecast_month) in detail_months_map:
                            j.confirmed_total_ws = detail_months_map[
                                str(j.forecast_month)
                            ]["total_ws_conf"]
                            j.confirmed_ws_gov = detail_months_map[
                                str(j.forecast_month)
                            ]["ws_gov_conf"]
                            j.confirmed_ws_priv = detail_months_map[
                                str(j.forecast_month)
                            ]["ws_priv_conf"]

        commit(request, Database.VEHICLE_ALLOCATION)

    def approve_allocation(
        self, request: Request, approval_request: ApprovalAllocationRequest
    ) -> None:
        forecast = self.forecast_repo.find_forecast(
            request, month=approval_request.month, year=approval_request.year
        )

        if forecast is None:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND, detail="Forecast is not found"
            )

        payload = {"data": []}

        for i in forecast.details:
            if i.deletable == 0:
                temp = {
                    "RECORD_ID": i.id,
                    "DEALER_FORECAST_ID": forecast.id,
                    "MODEL_VARIANT": i.model_id,
                }
                for j in i.months:
                    if j.deletable == 0:
                        temp[f"N{j.forecast_month}_HMSI_ALLOCATION"] = j.hmsi_allocation
                payload["data"].append(temp)

        self.forecast_repo.approve_allocation_data(
            request, payload, approval_request.month, approval_request.year
        )

    def archive_forecast(self, request: Request, forecast: Forecast):
        archive = ForecastArchive(
            record_id=forecast.id,
            name=forecast.name,
            month=forecast.month,
            year=forecast.year,
            dealer_id=forecast.dealer_id,
            confirmed_at=forecast.confirmed_at,
            created_by=forecast.created_by,
            updated_by=forecast.updated_by,
            deleted_by=forecast.deleted_by,
            created_at=forecast.created_at,
            updated_at=forecast.updated_at,
            deletable=forecast.deletable,
        )

        # self.forecast_repo.add_forecast_archive(request, data)
