import abc

from fastapi import Request, UploadFile

from src.domains.calculations.entities.va_slot_calculation_details import (
    SlotCalculationDetail,
)
from src.domains.calculations.entities.va_slot_calculations import SlotCalculation
from src.models.requests.calculation_request import (
    GetCalculationRequest,
    UpdateCalculationRequest,
)
from src.models.responses.basic_response import NoDataResponse
from src.models.responses.calculation_response import GetCalculationResponse


class ICalculationUseCase:
    @abc.abstractmethod
    def upsert_take_off_data(
        self, request: Request, file: UploadFile, month: int, year: int
    ) -> None:
        pass

    @abc.abstractmethod
    def upsert_bo_soa_oc_booking_prospect(
        self, request: Request, path: str, month: int, year: int
    ) -> None:
        pass

    @abc.abstractmethod
    def get_calculation_detail(
        self, request: Request, get_calculation_request: GetCalculationRequest
    ) -> GetCalculationResponse:
        pass

    @abc.abstractmethod
    def update_calculation_detail(
        self, request: Request, update_calculation_request: UpdateCalculationRequest
    ):
        pass


class ICalculationRepository:

    @abc.abstractmethod
    def find_calculation(
        self, request: Request, id: str = None, month: int = None, year: int = None
    ) -> SlotCalculation | None:
        pass

    @abc.abstractmethod
    def create_calculation(
        self, request: Request, calculation: SlotCalculation
    ) -> SlotCalculation:
        pass

    @abc.abstractmethod
    def create_calculation_detail(
        self, request: Request, calculation_detail: SlotCalculation
    ) -> None:
        pass

    @abc.abstractmethod
    def find_calculation_detail(
        self,
        request: Request,
        slot_calculation_id: str = None,
        model_id: str = None,
        forecast_month: int = None,
    ) -> SlotCalculationDetail | None:
        pass
