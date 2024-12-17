import re
from typing import List, Dict

import pandas
from fastapi import Depends, HTTPException, Request, UploadFile
import os
import http
import openpyxl
from src.domains.calculations.calculation_interface import (
    ICalculationRepository,
    ICalculationUseCase,
)
from src.domains.calculations.calculation_repository import CalculationRepository
from src.domains.calculations.entities.va_slot_calculation_details import (
    SlotCalculationDetail,
)
from src.domains.calculations.entities.va_slot_calculations import SlotCalculation
from src.domains.masters.entities.va_models import Model
from src.domains.masters.master_interface import IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.requests.calculation_request import GetCalculationRequest
from src.models.responses.basic_response import TextValueResponse
from src.models.responses.calculation_response import (
    GetCalculationDetailResponse,
    GetCalculationResponse,
    GetCalculationStockPilotResponse,
    GetCalculationDetailMonthsResponse,
)
from src.models.responses.master_response import (
    CategoryResponse,
    ModelResponse,
    SegmentResponse,
)
from src.shared.enums import Database
from src.shared.utils.database_utils import begin_transaction, commit
from src.shared.utils.date import get_month_difference, is_date_string_format
from src.shared.utils.excel import (
    get_header_column_index,
    get_worksheet,
    open_excel_workbook,
)
from src.shared.utils.file_utils import (
    clear_directory,
    get_file_extension,
    save_upload_file,
)
from src.shared.utils.storage_utils import is_file_exist
from src.shared.utils.xid import generate_xid
from pathlib import Path


class CalculationUseCase(ICalculationUseCase):

    def __init__(
        self,
        calculation_repo: ICalculationRepository = Depends(CalculationRepository),
        master_repository: IMasterRepository = Depends(MasterRepository),
    ):
        self.calculation_repo = calculation_repo
        self.master_repository = master_repository

    def upsert_bo_soa_oc_booking_prospect(
        self, request, file: str, month: int, year: int
    ):
        if not is_file_exist(file):
            raise HTTPException(
                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Excel file is not found",
            )

        df = pandas.read_excel(os.getcwd() + "/storage" + file)
        columns = [
            "SO Number",
            "Status SO",
            "Status Pilot",
            "Dealer",
            "Model",
            "Cat",
            "Region",
            "Customer Name",
            "Vin Year Rev",
            "SRC",
            "Source",
            "Year",
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

        calculation_details: List[SlotCalculationDetail] = []
        calculation_detail_map = {}

        model_dict: Dict[str, Model] = {}

        for idx, row in df.iterrows():
            so_number = row["SO Number"]
            status_so = row["Status SO"]
            status_pilot = row["Status Pilot"]
            dealer = row["Dealer"]
            model_id = row["Model"]
            cat = row["Cat"]
            region = row["Region"]
            customer_name = row["Customer Name"]
            vin_year_rev = row["Vin Year Rev"]
            src = row["SRC"]
            source = row["Source"]
            row_year = row["Year"]

            if model_id not in model_dict:
                model = self.master_repository.find_model(request, model_id)
                if model is None:
                    raise HTTPException(
                        http.HTTPStatus.BAD_REQUEST,
                        detail=f"Model {model_id} is not found",
                    )
                model_dict[model_id] = model

            model = model_dict[model_id]

            is_soa = (
                so_number[:2].upper() == "SO"
                and status_so.upper() == "ACCEPTED"
                and status_pilot.upper() == "PILOT"
                and source.upper() == "FCST ORDER"
            )

            is_so = (
                so_number[:2].upper() == "SO"
                and status_so.upper() == "PROSPECT"
                and status_pilot.upper() == "PILOT"
                and source.upper() == "FCST ORDER"
            )

            is_oc = (
                so_number[:2].upper() != "SO"
                and (status_so.upper() == "ACCEPTED" or status_so.upper() == "PROSPECT")
                and status_pilot.upper() == "PILOT"
                and source.upper() == "FCST ORDER"
            )

            is_booking = (
                so_number[:2].upper() != "SO" and source.upper() == "URGENT ORDER"
            )

            for j in forecast_months:
                forecast_month = get_month_difference(f"{year}-{month}", j)

                if forecast_month < 0:
                    raise HTTPException(
                        status_code=http.HTTPStatus.BAD_REQUEST,
                        detail=f"Forecast month cannot be less than the current month",
                    )

                if model.id not in calculation_detail_map:
                    calculation_detail_map[model.id] = {}

                if forecast_month not in calculation_detail_map[model.id]:
                    calculation_detail_map[model.id][forecast_month] = (
                        SlotCalculationDetail(
                            model_id=model.id,
                            forecast_month=forecast_month,
                            soa=0,
                            bo=0,
                            oc=0,
                            so=0,
                            booking_prospect=0,
                        )
                    )

                calculation_detail_map[model.id][forecast_month].soa += (
                    row[j] if is_soa and not pandas.isna(row[j]) else 0
                )
                calculation_detail_map[model.id][forecast_month].bo += 0
                calculation_detail_map[model.id][forecast_month].oc += (
                    row[j] if is_oc and not pandas.isna(row[j]) else 0
                )
                calculation_detail_map[model.id][forecast_month].so += (
                    row[j] if is_so and not pandas.isna(row[j]) else 0
                )
                calculation_detail_map[model.id][forecast_month].booking_prospect += (
                    row[j] if is_booking and not pandas.isna(row[j]) else 0
                )

        calculation = self.calculation_repo.find_calculation(
            request, month=month, year=year
        )

        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        if calculation is None:
            self.calculation_repo.create_calculation(
                request,
                SlotCalculation(month=month, year=year, details=calculation_details),
            )
        else:
            detail_maps = {}
            for i in calculation.details:
                if i.deletable == 0:
                    if i.model_id not in detail_maps:
                        detail_maps[i.model_id] = {}
                    if i.forecast_month not in detail_maps[i.model_id]:
                        detail_maps[i.model_id][i.forecast_month] = i

            for model_id, forecast_month_map in calculation_detail_map.items():
                if model_id in detail_maps:
                    for (
                        forecast_month,
                        calculation_detail,
                    ) in forecast_month_map.items():
                        calculation_detail.slot_calculation_id = calculation.id
                        if forecast_month not in detail_maps[model_id]:
                            self.calculation_repo.create_calculation_detail(
                                request, calculation_detail
                            )
                        else:
                            detail_maps[model_id][forecast_month].model_id = (
                                calculation_detail_map[model_id][
                                    forecast_month
                                ].model_id
                            )
                            detail_maps[model_id][forecast_month].soa = (
                                calculation_detail_map[model_id][forecast_month].soa
                            )
                            detail_maps[model_id][forecast_month].bo = (
                                calculation_detail_map[model_id][forecast_month].bo
                            )
                            detail_maps[model_id][forecast_month].oc = (
                                calculation_detail_map[model_id][forecast_month].oc
                            )
                            detail_maps[model_id][forecast_month].so = (
                                calculation_detail_map[model_id][forecast_month].so
                            )
                            detail_maps[model_id][forecast_month].booking_prospect = (
                                calculation_detail_map[model_id][
                                    forecast_month
                                ].booking_prospect
                            )
                else:
                    for (
                        forecast_month,
                        calculation_detail,
                    ) in forecast_month_map.items():
                        calculation_detail.slot_calculation_id = calculation.id
                        self.calculation_repo.create_calculation_detail(
                            request, calculation_detail
                        )

        commit(request, Database.VEHICLE_ALLOCATION)

    def upsert_take_off_data(
        self, request: Request, file: UploadFile, month: int, year: int
    ) -> None:

        begin_transaction(request, Database.VEHICLE_ALLOCATION)

        slot_calculation = self.calculation_repo.find_calculation(
            request, month=month, year=year
        )

        is_create = slot_calculation is None

        if is_create:
            slot_calculation = SlotCalculation()
            slot_calculation.month = month
            slot_calculation.year = year

            slot_calculation = self.calculation_repo.create_calculation(
                request, slot_calculation
            )

        temp_storage_path = f"{os.getcwd()}/src/temp"
        file_extension = get_file_extension(file)
        unique_filename = f"{generate_xid()}.{file_extension}"

        file_path = Path(temp_storage_path) / unique_filename

        save_upload_file(file, file_path)

        workbook = open_excel_workbook(file_path)
        worksheet = get_worksheet(workbook=workbook)

        HEADER_ROW_LOCATION = 1
        MODEL_NAME_COLUMN_NAME = "Sales Name"

        model_name_column_index = get_header_column_index(
            worksheet, MODEL_NAME_COLUMN_NAME, HEADER_ROW_LOCATION
        )

        if model_name_column_index is None:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=f"Column {MODEL_NAME_COLUMN_NAME} is not found",
            )
        new_calculation_details: List[SlotCalculationDetail] = []

        forecast_month_headers = [
            (cell.column, cell.value)
            for cell in worksheet[HEADER_ROW_LOCATION]
            if is_date_string_format(cell.value, "%Y-%m")
        ]

        for row in worksheet.iter_rows(
            min_row=HEADER_ROW_LOCATION + 1, max_row=worksheet.max_row
        ):
            model_name = row[model_name_column_index - 1].value
            model_detail = self.master_repository.find_model_by_variant(
                request, model_name
            )
            if model_detail is None:
                raise HTTPException(
                    status_code=http.HTTPStatus.NOT_FOUND,
                    detail=f"Model {model_name} is not found",
                )

            for column_index, header_name in forecast_month_headers:
                take_off_value = row[column_index - 1].value

                forecast_month = get_month_difference(f"{year}-{month}", header_name)

                if forecast_month < 0:
                    raise HTTPException(
                        status_code=http.HTTPStatus.BAD_REQUEST,
                        detail=f"Forecast month cannot be less than the current month",
                    )

                slot_calculation_detail = SlotCalculationDetail(
                    slot_calculation_id=slot_calculation.id,
                    model_id=model_detail.id,
                    forecast_month=forecast_month,
                    take_off=take_off_value,
                )

                new_calculation_details.append(slot_calculation_detail)

        if is_create:
            for calculation_detail in new_calculation_details:
                self.calculation_repo.create_calculation_detail(
                    request, calculation_detail
                )
        else:
            current_details = slot_calculation.details

            for i in range(len(new_calculation_details)):
                current_details[i].model_id = new_calculation_details[i].model_id
                current_details[i].forecast_month = new_calculation_details[
                    i
                ].forecast_month
                current_details[i].take_off = new_calculation_details[i].take_off

                self.calculation_repo.create_calculation_detail(
                    request, current_details[i]
                )
        commit(request, Database.VEHICLE_ALLOCATION)

        clear_directory(Path(temp_storage_path))

    def get_calculation_detail(
        self, request, get_calculation_request: GetCalculationRequest
    ) -> GetCalculationResponse | None:
        slot_calculation = self.calculation_repo.find_calculation(
            request,
            month=get_calculation_request.month,
            year=get_calculation_request.year,
        )

        if slot_calculation is None:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND, detail="Calculation not found"
            )

        model_map = {}

        for i in slot_calculation.details:
            if i.model_id not in model_map:
                model_map[i.model_id] = GetCalculationDetailMonthsResponse(
                    model_id=i.model_id,
                    months=[],
                    segment=TextValueResponse(
                        text=i.model.segment_id, value=i.model.segment_id
                    ),
                    category=TextValueResponse(
                        text=i.model.category_id, value=i.model.category_id
                    ),
                )

            model_map[i.model_id].months.append(
                GetCalculationDetailResponse(
                    month=i.forecast_month,
                    take_off=0 if i.take_off is None else i.take_off,
                    bo=0 if i.bo is None else i.bo,
                    soa=0 if i.soa is None else i.soa,
                    oc=0 if i.oc is None else i.oc,
                    booking_prospect=(
                        0 if i.booking_prospect is None else i.booking_prospect
                    ),
                )
            )

        models = []

        for k, v in model_map.items():
            models.append(v)

        return GetCalculationResponse(models=models)
