import http
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
import re
from typing import List, Dict
import requests

from src.config.config import get_config
from fastapi import Depends, HTTPException, UploadFile
import openpyxl
from starlette.requests import Request

from src.domains.calculations.calculation_interface import ICalculationRepository
from src.domains.calculations.calculation_repository import CalculationRepository
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
from src.shared.utils.parser import to_dict
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

        if forecast is not None:
            self.archive_forecast(request, forecast)
            self.forecast_repo.delete_forecast(request, forecast)

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

        forecast.details = list(new_details.values())
        self.forecast_repo.create_forecast(request, forecast)
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

        order_confirmation_date = (
            data.confirmed_at.strftime("%m/%d/%Y")
            if data.confirmed_at is not None
            else "N/A"
        )

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
                    category=TextValueResponse(
                        text=i.model.category_id,
                        value=i.model.category_id,
                    ),
                    months=months,
                )
            )

        return GetForecastResponse(
            id=data.id,
            order_confirmation_date=order_confirmation_date,
            month=data.month,
            year=data.year,
            dealer=TextValueResponse(text=data.dealer.name, value=data.dealer.id),
            models=sorted(models, key=lambda x: (x.category.text, x.model.text)),
        )

    def confirm_forecast(
        self, request: Request, confirm_request: ConfirmForecastRequest
    ) -> str:
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
        return forecast.dealer_id

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
        )

        archive_details = []
        archive_month_details = []

        for i in forecast.details:
            archive_details.append(
                ForecastDetailArchive(
                    record_id=i.id,
                    model_id=i.model_id,
                    end_stock=i.end_stock,
                    forecast_id=i.forecast_id,
                    created_by=i.created_by,
                    updated_by=i.updated_by,
                    deleted_by=i.deleted_by,
                    created_at=i.created_at,
                    updated_at=i.updated_at,
                )
            )

            for j in i.months:
                archive_month_details.append(
                    ForecastDetailMonthArchive(
                        record_id=j.id,
                        forecast_month=j.forecast_month,
                        forecast_detail_id=j.forecast_detail_id,
                        rs_gov=j.rs_gov,
                        ws_gov=j.ws_gov,
                        rs_priv=j.rs_priv,
                        ws_priv=j.ws_priv,
                        total_rs=j.total_rs,
                        prev_rs_gov=j.prev_rs_gov,
                        prev_rs_priv=j.prev_rs_priv,
                        total_prev_rs=j.total_prev_rs,
                        total_ws=j.total_ws,
                        total_prev_final_conf_allocation=j.total_prev_final_conf_allocation,
                        new_ws_req=j.new_ws_req,
                        hmsi_allocation=j.hmsi_allocation,
                        created_by=j.created_by,
                        updated_by=j.updated_by,
                        deleted_by=j.deleted_by,
                        created_at=j.created_at,
                        updated_at=j.updated_at,
                    )
                )

        self.forecast_repo.add_forecast_archive(
            request, archive, archive_details, archive_month_details
        )

    def generate_forecast_pdf(
        self, request: Request, get_pdf_request: GetForecastDetailRequest
    ) -> str:
        try:
            forecast = self.get_forecast_detail(
                request,
                get_pdf_request,
            )

            forecast_data_dict = forecast.model_dump()

            res = requests.post(
                "{}/pdf/vehicle-allocation/oc?api_key={}".format(
                    get_config().outbound["pdf"].base_url,
                    get_config().outbound["pdf"].api_key,
                ),
                json={"data": forecast_data_dict},
                timeout=10,
                headers={"Content-Type": "application/json"},
            )

            if res.status_code != 200:
                raise HTTPException(
                    status_code=res.status_code, detail="Failed to generate pdf"
                )

            return res.text
        except requests.exceptions.Timeout as e:
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Outbound Timeout: pdf/vehicle-allocation/oc",
            )
