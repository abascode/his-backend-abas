

import abc

from fastapi import Request, UploadFile

from src.domains.calculations.entities.va_slot_calculations import SlotCalculation
from src.models.responses.basic_response import NoDataResponse


class ICalculationUseCase:
    @abc.abstractmethod
    def upsert_take_off_data(self,request: Request, take_off_data: UploadFile, month: int, year: int) -> None:
        pass
    
    @abc.abstractmethod
    def upsert_bo_soa_oc_booking_prospect(self,request: Request, bo_soa_oc_booking_prospect_data: UploadFile, month: int, year: int) -> None:
        pass
    
   
    
class ICalculationRepository:
    
    @abc.abstractmethod
    def find_calculation(self, request: Request, id: str = None, month: str = None, year: int = None) -> SlotCalculation | None:
        pass
    
    @abc.abstractmethod
    def create_calculation(self, request: Request, calculation: SlotCalculation) -> SlotCalculation:
        pass
    
    @abc.abstractmethod
    def create_calculation_detail(self, request: Request, calculation_detail: SlotCalculation) -> None:
        pass