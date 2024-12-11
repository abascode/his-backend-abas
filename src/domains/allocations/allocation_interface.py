import abc
from typing import List

from starlette.requests import Request

from src.models.requests.allocation_request import GetAllocationRequest
from src.models.responses.allocation_response import GetAllocationResponse


class IAllocationUseCase:
    @abc.abstractmethod
    def get_allocations(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> List[GetAllocationResponse]:
        pass


class IAllocationRepository:
    @abc.abstractmethod
    def get_allocation_adjustments(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> tuple:
        pass
