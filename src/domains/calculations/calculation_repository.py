from fastapi import Depends, Request
from sqlalchemy.orm import Session

from src.domains.calculations.calculation_interface import ICalculationRepository
from src.dependencies.database_dependency import get_va_db
from src.domains.calculations.entities.va_slot_calculation_details import (
    SlotCalculationDetail,
)
from src.domains.calculations.entities.va_slot_calculations import SlotCalculation


class CalculationRepository(ICalculationRepository):

    def __init__(self, va_db: Session = Depends(get_va_db)):
        self.va_db = va_db

    def get_va_db(self, request: Request) -> Session:
        return request.state.va_db if request.state.va_db is not None else self.va_db

    def find_calculation(
        self,
        request: Request,
        id: str = None,
        month: str = None,
        year: int = None,
    ) -> SlotCalculation | None:
        query = (
            self.get_va_db(request)
            .query(SlotCalculation)
            .filter(SlotCalculation.deletable == 0)
        )

        if id is not None:
            query = query.filter(SlotCalculation.id == id)

        if month is not None:
            query = query.filter(SlotCalculation.month == month)

        if year is not None:
            query = query.filter(SlotCalculation.year == year)

        return query.first()

    def create_calculation(
        self, request: Request, calculation: SlotCalculation
    ) -> SlotCalculation:
        self.get_va_db(request).add(calculation)
        self.get_va_db(request).flush()

        return calculation

    def create_calculation_detail(
        self, request: Request, calculation_detail: SlotCalculationDetail
    ) -> None:
        self.get_va_db(request).add(calculation_detail)
        self.get_va_db(request).flush()
