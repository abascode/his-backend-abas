

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
from src.shared.enums import Database
from src.shared.utils.database_utils import begin_transaction, commit
from src.shared.utils.date import is_year_month
from src.shared.utils.excel import get_header_column_index, get_worksheet, open_excel_workbook
from src.shared.utils.file_utils import clear_directory, get_file_extension, save_upload_file
from src.shared.utils.xid import generate_xid
from pathlib import Path


class CalculationUseCase(ICalculationUseCase):
    
    def __init__(self, calculation_repo: ICalculationRepository = Depends(CalculationRepository),master_repository: IMasterRepository = Depends(MasterRepository)):
        self.calculation_repo = calculation_repo
        self.master_repository = master_repository
        
    #TODO : waiting template finalization
    def upsert_bo_soa_oc_booking_prospect(self, request, bo_soa_oc_booking_prospect_data: UploadFile, month: int, year: int):
        begin_transaction(request, Database.VEHICLE_ALLOCATION)
        
        slot_calculation = self.calculation_repo.find_calculation(request, month=month, year=year)
        
        is_create = slot_calculation.details is None or len(slot_calculation.details) == 0
        
        pass
            
    def upsert_take_off_data(self,request: Request, take_off_data: UploadFile, month: int, year: int) -> None:
        
        begin_transaction(request, Database.VEHICLE_ALLOCATION)
        
        slot_calculation = self.calculation_repo.find_calculation(request, month=month, year=year)
        
        is_create = slot_calculation is None
        
        
        if is_create:
            slot_calculation = SlotCalculation()
            slot_calculation.month = month
            slot_calculation.year = year
            
            slot_calculation = self.calculation_repo.create_calculation(request, slot_calculation)
        
        
        temp_storage_path = f"{os.getcwd()}/src/temp"
        file_extension = get_file_extension(take_off_data)
        unique_filename = f"{generate_xid()}.{file_extension}"
        
        file_path = Path(temp_storage_path) / unique_filename
        
        save_upload_file(take_off_data, file_path)
        
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
            if is_year_month(cell.value)
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
                
                _, month = header_name.split("-")
                
                slot_calculation_detail = SlotCalculationDetail(
                    slot_calculation_id = slot_calculation.id,
                    model_id = model_detail.id,
                    forecast_month = month,
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
        
        
        
        
        
        
        