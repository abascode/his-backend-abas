import http
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import openpyxl
import pandas
from fastapi import Depends, HTTPException, UploadFile
from openpyxl.styles import Border, Side, Alignment
from openpyxl.workbook import Workbook
from starlette.requests import Request
from src.domains.allocations.allocation_interface import (
    IAllocationRepository,
    IAllocationUseCase,
)
from src.domains.allocations.allocation_repository import AllocationRepository
from src.domains.allocations.entities.allocation_approvals import AllocationApproval
from src.domains.allocations.enums import (
    AllocationSubmissionStatusEnum,
    AllocationApprovalFlagEnum,
)
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.domains.forecasts.forecast_interface import IForecastRepository
from src.domains.forecasts.forecast_repository import ForecastRepository
from src.domains.masters.entities.va_categories import Category
from src.domains.masters.entities.va_dealers import Dealer
from src.domains.masters.master_interface import IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.domains.users.enums import RoleDict
from src.models.requests.allocation_request import (
    GetAllocationRequest,
    SubmitAllocationRequest,
    SubmitAllocationAdjustmentRequest,
)
from src.models.requests.forecast_request import ApprovalAllocationRequest
from src.models.responses.allocation_response import (
    GetAllocationAdjustmentResponse,
    AllocationAdjustmentMonthResponse,
    AllocationAdjustmentModelResponse,
    AllocationTargetMonthCategoryResponse,
    GetAllocationResponse,
    AllocationTargetMonthMonthResponse,
    AllocationTargetMonthResponse,
    AllocationApprovalResponse,
)
from src.models.responses.basic_response import TextValueResponse
from src.shared.enums import Database
from src.shared.utils.database_utils import commit, begin_transaction
from src.shared.utils.date import is_date_string_format, get_month_difference
from src.shared.utils.excel import get_header_column_index
from src.shared.utils.file_utils import (
    clear_directory,
    save_upload_file,
    get_file_extension,
)
from src.shared.utils.storage_utils import get_full_path, is_file_exist
from src.shared.utils.xid import generate_xid


class AllocationUseCase(IAllocationUseCase):
    def __init__(
        self,
        allocation_repo: IAllocationRepository = Depends(AllocationRepository),
        master_repo: IMasterRepository = Depends(MasterRepository),
        forecast_repo: IForecastRepository = Depends(ForecastRepository),
    ):
        self.master_repo = master_repo
        self.allocation_repo = allocation_repo
        self.forecast_repo = forecast_repo

    def get_allocations(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> GetAllocationResponse:
        adjustment_data = self.allocation_repo.get_allocation_adjustments(
            request, get_allocation_request
        )
        monthly_target_data = self.allocation_repo.get_allocation_monthly_target(
            request, get_allocation_request
        )

        approval_data = self.allocation_repo.get_allocation_approvals(
            request, get_allocation_request.month, get_allocation_request.year
        )

        approvals = [
            AllocationApprovalResponse(
                id=i.id,
                approver=(
                    TextValueResponse(text=i.approver.id, value=i.approver.name)
                    if i.approver is not None
                    else None
                ),
                approved_at=i.approved_at,
                approved_comment=i.approved_comment,
                approval_flag=i.approval_flag,
                role=TextValueResponse(
                    text=RoleDict.get(i.role_id, "-"), value=i.role_id
                ),
            )
            for i in approval_data
        ]

        total_alloc_map = {}
        dealer_adjustment_map = {}
        model_map = {}
        dealer_map = {}

        for i in adjustment_data:
            (
                forecast_detail_month_id,
                dealer_id,
                dealer,
                year,
                month,
                model_id,
                segment_id,
                category_id,
                forecast_month,
                adjustment_model,
                ws,
                ws_percentage,
                allocation,
                confirmed_total_ws,
                end_stock,
            ) = i

            if dealer_id not in dealer_map:
                dealer_map[dealer_id] = dealer

            if dealer_id not in dealer_adjustment_map:
                dealer_adjustment_map[dealer_id] = {}

            if model_id not in dealer_adjustment_map[dealer_id]:
                dealer_adjustment_map[dealer_id][model_id] = {}

            if dealer_id not in total_alloc_map:
                total_alloc_map[dealer_id] = {}

            if model_id not in model_map:
                model_map[model_id] = {
                    "segment_id": segment_id,
                    "category_id": category_id,
                }

            if category_id not in total_alloc_map[dealer_id]:
                total_alloc_map[dealer_id][category_id] = 0

            allocation = min(allocation, ws)

            total_alloc_map[dealer_id][category_id] += allocation
            dealer_adjustment_map[dealer_id][model_id]["remaining_stock"] = end_stock
            dealer_adjustment_map[dealer_id][model_id][forecast_month] = (
                AllocationAdjustmentMonthResponse(
                    id=forecast_detail_month_id,
                    month=forecast_month,
                    adjustment=adjustment_model,
                    ws=ws,
                    ws_percentage=ws_percentage,
                    allocation=allocation,
                    confirmed_total_ws=confirmed_total_ws,
                )
            )

        adjustments = []

        for dealer_id, dealer_adjustment_model in dealer_adjustment_map.items():
            adjustment = GetAllocationAdjustmentResponse(
                dealer=TextValueResponse(text=dealer_map[dealer_id], value=dealer_id),
                models=[],
            )

            for model_id, forecast_month_map in dealer_adjustment_map[
                dealer_id
            ].items():
                adjustment_model = AllocationAdjustmentModelResponse(
                    model=TextValueResponse(text=model_id, value=model_id),
                    remaining_stock=forecast_month_map["remaining_stock"],
                    category=TextValueResponse(
                        text=model_map[model_id]["category_id"],
                        value=model_map[model_id]["category_id"],
                    ),
                    segment=TextValueResponse(
                        text=model_map[model_id]["segment_id"],
                        value=model_map[model_id]["segment_id"],
                    ),
                    months=[],
                )

                for forecast_month, month in forecast_month_map.items():
                    if forecast_month != "remaining_stock":
                        adjustment_model.months.append(month)

                adjustment.models.append(adjustment_model)
            adjustments.append(adjustment)

        monthly_target_map = {}
        category_target = {}

        for (
            category_id,
            target,
            dealer_id,
            forecast_month,
            alloc_prev_month,
            ws,
        ) in monthly_target_data:
            total_alloc = total_alloc_map.get(dealer_id, {}).get(category_id, 0)
            vs_target = int(total_alloc / (target * 100)) if target else 0
            vs_forecast = int(total_alloc / (ws * 100)) if ws else 0

            if dealer_id not in monthly_target_map:
                monthly_target_map[dealer_id] = {}

            if category_id not in monthly_target_map[dealer_id]:
                monthly_target_map[dealer_id][category_id] = []

            if forecast_month not in category_target:
                category_target[category_id] = 0

            category_target[category_id] += target

            monthly_target_map[dealer_id][category_id].append(
                AllocationTargetMonthMonthResponse(
                    month=forecast_month,
                    target=target,
                    percentage=0,
                    alloc_prev_month=alloc_prev_month,
                    ws=ws,
                    total_alloc=total_alloc,
                    vs_target=vs_target,
                    vs_forecast=vs_forecast,
                )
            )

        targets = []
        for dealer_id, category_map in monthly_target_map.items():
            target = AllocationTargetMonthResponse(
                dealer=TextValueResponse(
                    text=dealer_map.get(dealer_id, "-"), value=dealer_id
                ),
                categories=[],
            )

            for category_id, months in category_map.items():
                for i in months:
                    i.percentage = int(i.target / category_target[category_id] * 100)

                target.categories.append(
                    AllocationTargetMonthCategoryResponse(
                        category=TextValueResponse(text=category_id, value=category_id),
                        months=months,
                    )
                )

            targets.append(target)

        return GetAllocationResponse(
            approvals=approvals, adjustments=adjustments, targets=targets
        )

    def upsert_monthly_target(self, request, file: str, month: int, year: int):
        if not is_file_exist(file):
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Excel file is not found",
            )

        df = pandas.read_excel(os.getcwd() + "/storage" + file)
        columns = [
            "Dealer Name",
            "Category",
        ]

        not_found_index = [i for i in columns if i not in df.columns.tolist()]
        forecast_months = [
            i for i in df.columns.tolist() if re.match(r"^\d{4}-(0[1-9]|1[0-2])$", i)
        ]

        if len(not_found_index) > 0:
            raise HTTPException(
                http.HTTPStatus.BAD_REQUEST,
                detail=f"{not_found_index[0]} field is required.",
            )

        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        dealer_dict: Dict[str, Dealer] = {}
        category_dict: Dict[str, Category] = {}
        monthly_target_details: List[MonthlyTargetDetail] = []
        monthly_target_map = {}

        for idx, row in df.iterrows():
            dealer_id = row["Dealer Name"]
            category_id = row["Category"]

            if dealer_id not in dealer_dict:
                dealer = self.master_repo.find_dealer(request, dealer_id=dealer_id)
                if dealer is None:
                    raise HTTPException(
                        status_code=http.HTTPStatus.BAD_REQUEST,
                        detail=f"Dealer {dealer_id} is not found",
                    )
                dealer_dict[dealer_id] = dealer

            if category_id not in category_dict:
                category = self.master_repo.find_category(request, category_id)
                if category is None:
                    raise HTTPException(
                        status_code=http.HTTPStatus.BAD_REQUEST,
                        detail=f"Category {category_id} is not found",
                    )
                category_dict[category_id] = category

            dealer = dealer_dict[dealer_id]
            category = category_dict[category_id]

            for j in forecast_months:
                forecast_month = get_month_difference(f"{year}-{month}", j)

                if forecast_month < 0:
                    raise HTTPException(
                        status_code=http.HTTPStatus.BAD_REQUEST,
                        detail=f"Forecast month cannot be less than the current month",
                    )

                monthly_target = MonthlyTargetDetail(
                    forecast_month=forecast_month,
                    dealer_id=dealer.id,
                    target=row[j] if not pandas.isna(row[j]) else 0,
                    category_id=category.id,
                )

                monthly_target_details.append(monthly_target)
                monthly_target_map[(dealer_id, category_id, forecast_month)] = (
                    monthly_target
                )

        monthly_target = self.allocation_repo.find_monthly_target(
            request, month=month, year=year
        )

        if monthly_target is None:
            monthly_target = MonthlyTarget(
                month=month, year=year, details=monthly_target_details
            )
            self.allocation_repo.create_monthly_target(request, monthly_target)
        else:
            detail_maps = {}

            for i in monthly_target.details:
                if i.deletable == 0:
                    detail_maps[(i.dealer_id, i.category_id, i.forecast_month)] = i

            for k, v in monthly_target_map.items():
                dealer_id, category_id, forecast_month = k
                if (dealer_id, category_id, forecast_month) not in detail_maps:
                    v.month_target_id = monthly_target.id
                    self.allocation_repo.create_monthly_target_detail(request, v)
                else:
                    detail = detail_maps[(dealer_id, category_id, forecast_month)]
                    detail.target = v.target

        commit(request, Database.VEHICLE_ALLOCATION)

    def submit_allocation(
        self, request: Request, submit_allocation_request: SubmitAllocationRequest
    ) -> None:
        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        forecasts = self.forecast_repo.get_forecast(
            request,
            month=submit_allocation_request.month,
            year=submit_allocation_request.year,
        )

        if len(forecasts) == 0:
            raise HTTPException(
                http.HTTPStatus.BAD_REQUEST, detail="Forecast is not found"
            )

        adjustment_map: Dict[str, SubmitAllocationAdjustmentRequest] = {}

        for i in submit_allocation_request.adjustments:
            adjustment_map[i.forecast_detail_month_id] = i

        for i in forecasts:
            for j in i.details:
                if j.deletable == 0:
                    for k in j.months:
                        if k.deletable == 0:
                            if k.id in adjustment_map:
                                k.adjustment = adjustment_map[k.id].adjustment
                                k.hmsi_allocation = adjustment_map[k.id].hmsi_allocation

        if submit_allocation_request.status == AllocationSubmissionStatusEnum.SUBMIT:
            approvals = self.allocation_repo.get_allocation_approvals(
                request, submit_allocation_request.month, submit_allocation_request.year
            )
            if len(approvals) == 0:
                matrices = self.allocation_repo.get_allocation_approval_matrices(
                    request,
                )
                approvals = []
                for i in matrices:
                    approvals.append(
                        AllocationApproval(
                            month=submit_allocation_request.month,
                            year=submit_allocation_request.year,
                            approval_flag=AllocationApprovalFlagEnum.WAITING,
                            role_id=i.role_id,
                        )
                    )
                approvals[0].approver_id = request.state.user.username
                approvals[0].approval_flag = AllocationApprovalFlagEnum.SUBMITTED
                approvals[0].approved_at = datetime.now()

                self.allocation_repo.create_allocation_approvals(request, approvals)

        commit(request, Database.VEHICLE_ALLOCATION)

    def approve_allocation(
        self, request: Request, approval_request: ApprovalAllocationRequest
    ) -> dict:

        begin_transaction(request, Database.VEHICLE_ALLOCATION)
        forecasts = self.forecast_repo.get_forecast(
            request, month=approval_request.month, year=approval_request.year
        )

        if len(forecasts) is None:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND, detail="Forecast is not found"
            )

        approvals = self.allocation_repo.get_allocation_approvals(
            request, approval_request.month, approval_request.year
        )

        if len(approvals) == 0:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail="Allocation is not submitted",
            )

        unapproved_approvals = [i for i in approvals if i.approved_at is None]

        if len(unapproved_approvals) > 0:
            if unapproved_approvals[0].role_id not in request.state.user.role_id:
                raise HTTPException(
                    status_code=http.HTTPStatus.FORBIDDEN,
                    detail="You are not authorized to approve this allocation",
                )
            else:
                unapproved_approvals[0].approved_at = datetime.now()
                unapproved_approvals[0].approver_id = request.state.user.username
                unapproved_approvals[0].approval_flag = (
                    AllocationApprovalFlagEnum.APPROVED
                )

        unapproved_approvals = [i for i in approvals if i.approved_at is None]

        if len(unapproved_approvals) == 0:
            payload = {"data": []}
            for forecast in forecasts:
                for i in forecast.details:
                    if i.deletable == 0:
                        temp = {
                            "RECORD_ID": i.id,
                            "DEALER_FORECAST_ID": forecast.id,
                            "MODEL_VARIANT": i.model_id,
                        }
                        for j in i.months:
                            if j.deletable == 0:
                                temp[f"N{j.forecast_month}_HMSI_ALLOCATION"] = (
                                    j.hmsi_allocation
                                )
                        payload["data"].append(temp)

            data = self.allocation_repo.approve_allocation_data(request, payload)
            commit(request, Database.VEHICLE_ALLOCATION)

            return {
                "payload": payload,
                "response": data,
            }

        commit(request, Database.VEHICLE_ALLOCATION)

        return {
            "message": "Success approving allocation",
        }

    def download_monthly_target_excel_template(
        self, request: Request, month: int, year: int
    ) -> str:
        workbook = Workbook()

        sheet = workbook.active
        sheet.title = "Template-Monthly target"

        headers = ["Dealer name", "Category"]

        for i in range(12):
            if i > 0:
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            headers.append(f"{year}-{month:02}")

        for col_index, header in enumerate(headers, start=1):
            cell = sheet.cell(row=1, column=col_index, value=header)
            thin_border = Border(
                left=Side(style="thin"),
                right=Side(style="thin"),
                top=Side(style="thin"),
                bottom=Side(style="thin"),
            )
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center")
            sheet.column_dimensions[cell.column_letter].width = len(header) + 2

        relative_path = (
            "/temp/template/allocations/monthly-target-" + str(uuid.uuid4()) + ".xlsx"
        )
        dest = get_full_path(relative_path)
        upload_dir = os.path.join(os.getcwd(), "storage/temp/template/allocations")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        workbook.save(dest)
        return dest
