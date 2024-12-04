

from typing import List
from fastapi import Depends, HTTPException, Request, UploadFile
import os
import http
import openpyxl
from src.domains.calculations.calculation_interface import ICalculationRepository, ICalculationUseCase
from src.domains.calculations.calculation_repository import CalculationRepository
from src.domains.calculations.entities.va_slot_calculation_details import SlotCalculationDetail
from src.domains.calculations.entities.va_slot_calculations import SlotCalculation
from src.domains.masters.master_interface import IMasterRepository
from src.domains.masters.master_repository import MasterRepository
from src.models.responses.calculation_response import GetCalculationDetailResponse, GetCalculationResponse, GetCalculationStockPilotResponse
from src.models.responses.master_response import CategoryResponse, ModelResponse, SegmentResponse
from src.shared.enums import Database
from src.shared.utils.database_utils import begin_transaction, commit
from src.shared.utils.date import get_month_difference, is_date_string_format
from src.shared.utils.excel import get_header_column_index, get_worksheet, open_excel_workbook
from src.shared.utils.file_utils import clear_directory, get_file_extension, save_upload_file
from src.shared.utils.xid import generate_xid
from pathlib import Path


class CalculationUseCase(ICalculationUseCase):
    
    def __init__(self, calculation_repo: ICalculationRepository = Depends(CalculationRepository),master_repository: IMasterRepository = Depends(MasterRepository)):
        self.calculation_repo = calculation_repo
        self.master_repository = master_repository
        
    #TODO : waiting template finalization
    def upsert_bo_soa_oc_booking_prospect(self, request, file: UploadFile, month: int, year: int):
        begin_transaction(request, Database.VEHICLE_ALLOCATION)
        
        slot_calculation = self.calculation_repo.find_calculation(request, month=month, year=year)
        
        is_create = slot_calculation.details is None or len(slot_calculation.details) == 0
        
        pass
            
    def upsert_take_off_data(self,request: Request, file: UploadFile, month: int, year: int) -> None:
        
        begin_transaction(request, Database.VEHICLE_ALLOCATION)
        
        slot_calculation = self.calculation_repo.find_calculation(request, month=month, year=year)
        
        is_create = slot_calculation is None
    
        if is_create:
            slot_calculation = SlotCalculation()
            slot_calculation.month = month
            slot_calculation.year = year
            
            slot_calculation = self.calculation_repo.create_calculation(request, slot_calculation)
        
        
        temp_storage_path = f"{os.getcwd()}/src/temp"
        file_extension = get_file_extension(file)
        unique_filename = f"{generate_xid()}.{file_extension}"
        
        file_path = Path(temp_storage_path) / unique_filename
        
        save_upload_file(file, file_path)
        
        workbook = open_excel_workbook(file_path)
        worksheet = get_worksheet(workbook=workbook)
        
        HEADER_ROW_LOCATION = 1
        MODEL_NAME_COLUMN_NAME = "Sales Name"
        
    
        model_name_column_index = get_header_column_index(worksheet, MODEL_NAME_COLUMN_NAME, HEADER_ROW_LOCATION)
        
        if model_name_column_index is None:
            raise HTTPException(
                status_code=http.HTTPStatus.BAD_REQUEST,
                detail=f"Column {MODEL_NAME_COLUMN_NAME} is not found",
            )        
        new_calculation_details: List[SlotCalculationDetail] = []
        
    
        forecast_month_headers = [
            (cell.column,cell.value) for cell in worksheet[HEADER_ROW_LOCATION]
            if is_date_string_format(cell.value, "%Y-%m")
        ]
        
        for row in worksheet.iter_rows(min_row=HEADER_ROW_LOCATION + 1, max_row=worksheet.max_row):
            model_name = row[model_name_column_index - 1].value
            model_detail = self.master_repository.find_model_by_variant(request, model_name)
            if model_detail is None:
                raise HTTPException(
                    status_code=http.HTTPStatus.NOT_FOUND,
                    detail=f"Model {model_name} is not found",
                )

            for column_index, header_name in forecast_month_headers:
                take_off_value = row[column_index - 1].value
                
                forecast_month = get_month_difference(
                    f"{year}-{month}", header_name
                )
                
                if forecast_month < 0:
                    raise HTTPException(
                        status_code=http.HTTPStatus.BAD_REQUEST,
                        detail=f"Forecast month cannot be less than the current month",
                    )
                
                slot_calculation_detail = SlotCalculationDetail(
                    slot_calculation_id = slot_calculation.id,
                    model_id = model_detail.id,
                    forecast_month = forecast_month,
                    take_off= take_off_value,
                )
                
                new_calculation_details.append(
                    slot_calculation_detail
                )
                
        if is_create:
            for calculation_detail in new_calculation_details:
                self.calculation_repo.create_calculation_detail(request, calculation_detail)
        else:
            current_details = slot_calculation.details
            
            for i in range(len(new_calculation_details)):
                current_details[i].model_id = new_calculation_details[i].model_id
                current_details[i].forecast_month = new_calculation_details[i].forecast_month
                current_details[i].take_off = new_calculation_details[i].take_off
                
                self.calculation_repo.create_calculation_detail(request, current_details[i])
        commit(request, Database.VEHICLE_ALLOCATION)
            
        clear_directory(Path(temp_storage_path))
    
    def get_calculation_detail(self, request, get_calculation_request)-> GetCalculationResponse | None:
        slot_calculation = self.calculation_repo.find_calculation(request, month=get_calculation_request.month, year=get_calculation_request.year)
        
        if slot_calculation is None:
            raise HTTPException(
                status_code=http.HTTPStatus.NOT_FOUND,
                detail="Calculation not found"
            )
            
        details: List[GetCalculationDetailResponse] = []
        
        for i in range(len(slot_calculation.details)):
            detail = slot_calculation.details[i]
            category: CategoryResponse= CategoryResponse(
                id=detail.model.category.id
            )
            
            segment: SegmentResponse = SegmentResponse(
                id=detail.model.segment.id
            )
            model: ModelResponse = ModelResponse(
                id = detail.model.id,
                manufacturer_code = detail.model.manufacture_code,
                group = detail.model.group,
                category = category,
                segment = segment,
                usage = detail.model.usage,
                euro = detail.model.euro
            )
            details.append(
                GetCalculationDetailResponse(
                    model = model,
                    forecast_month = detail.forecast_month,
                    take_off = detail.take_off if detail.take_off is not None else 0,

                    bo= detail.bo if detail.bo is not None else 0,
                    soa= detail.soa if detail.soa is not None else 0,
                    oc= detail.oc if detail.oc is not None else 0,
                    booking_prospect= detail.booking_prospect if detail.booking_prospect is not None else 0
                )
            )
            
        stock_pilots: List[GetCalculationStockPilotResponse] = []
        
        for i in range(len(slot_calculation.stock_pilots)):
            segment = SegmentResponse(
                id = slot_calculation.stock_pilots[i].segment
            )
            
            stock_pilots.append(
                GetCalculationStockPilotResponse(
                    segment = segment,
                    percentage = slot_calculation.stock_pilots[i].percentage
                )
            )
        
        return GetCalculationResponse(
            id = slot_calculation.id,
            month = slot_calculation.month,
            year = slot_calculation.year,
            details = details,
            stock_pilots = stock_pilots
        )
        
        
        
        
        
        
        
        
        