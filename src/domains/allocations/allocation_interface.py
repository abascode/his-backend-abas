import abc
from typing import List

from fastapi import UploadFile
from starlette.requests import Request

from src.domains.allocations.entities.allocation_approval_matrix import (
    AllocationApprovalMatrix,
)
from src.domains.allocations.entities.allocation_approvals import AllocationApproval
from src.domains.forecasts.entities.va_monthly_target_details import MonthlyTargetDetail
from src.domains.forecasts.entities.va_monthly_targets import MonthlyTarget
from src.models.requests.allocation_request import (
    GetAllocationRequest,
    SubmitAllocationRequest,
)
from src.models.requests.forecast_request import ApprovalAllocationRequest
from src.models.responses.allocation_response import GetAllocationAdjustmentResponse


class IAllocationUseCase:
    @abc.abstractmethod
    def get_allocations(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> List[GetAllocationAdjustmentResponse]:
        pass

    @abc.abstractmethod
    def upsert_monthly_target(
        self, request: Request, file: UploadFile, month: int, year: int
    ) -> None:
        pass

    @abc.abstractmethod
    def submit_allocation(
        self, request: Request, submit_allocation_request: SubmitAllocationRequest
    ) -> None:
        pass

    @abc.abstractmethod
    def approve_allocation(
        self, request: Request, approval_request: ApprovalAllocationRequest
    ):
        pass


class IAllocationRepository:
    @abc.abstractmethod
    def get_allocation_adjustments(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> tuple:
        pass

    @abc.abstractmethod
    def get_allocation_monthly_target(
        self, request: Request, get_allocation_request: GetAllocationRequest
    ) -> tuple:
        pass

    @abc.abstractmethod
    def find_monthly_target(
        self,
        request: Request,
        monthly_target_id: str = None,
        month: int = None,
        year: int = None,
    ) -> MonthlyTarget | None:
        pass

    @abc.abstractmethod
    def create_monthly_target(
        self, request: Request, monthly_target: MonthlyTarget
    ) -> MonthlyTarget:
        pass

    @abc.abstractmethod
    def create_monthly_target_detail(
        self, request: Request, monthly_target_detail: MonthlyTargetDetail
    ) -> MonthlyTargetDetail:
        pass

    @abc.abstractmethod
    def get_allocation_approvals(
        self, request: Request, month: int, year: int
    ) -> List[AllocationApproval]:
        pass

    @abc.abstractmethod
    def get_allocation_approval_matrices(
        self, request: Request
    ) -> List[AllocationApprovalMatrix]:
        pass

    @abc.abstractmethod
    def create_allocation_approvals(
        self, request: Request, approvals: List[AllocationApproval]
    ):
        pass

    @abc.abstractmethod
    def approve_allocation_data(
        self,
        request: Request,
        payload: dict,
    ):
        pass
